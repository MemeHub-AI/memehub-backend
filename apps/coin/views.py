from decimal import Decimal
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from . import models, serializers
from apps.user import models as user_models
from django.db.models import Q
from django.conf import settings
from django.core.cache import cache
from extension.auth import JWTHeadersAuthentication, MyAuthenticationFailed
from django.contrib.auth.models import AnonymousUser

# Create your views here.

class CoinListPagination(PageNumberPagination):
    page_size = settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = settings.MAX_PAGE_SIZE


class CoinListView(generics.ListAPIView):
    queryset = models.Coin.objects.all().order_by('-id')
    serializer_class = serializers.CoinSerializer
    pagination_class = CoinListPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        token = self.request.query_params.get('token', None)
        queryset = queryset.filter(status=1)
        if token:
            token = token.lower()
            queryset = queryset.filter(
                Q(name__icontains=token) | Q(ticker__icontains=token)
            )

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            paginated_response = self.get_paginated_response(serializer.data)
            paginated_response.data = {"code": 200, "message": "ok", "data": paginated_response.data}
            return paginated_response

        serializer = self.get_serializer(queryset, many=True)
        return Response({"code": 200,"message": "ok","data": serializer.data})


class CoinAPIView(APIView):
    authentication_classes = [JWTHeadersAuthentication,]
    
    def get(self, request, address=None):
        if address:
            try:
                coin = models.Coin.objects.get(address=address)
            except models.Coin.DoesNotExist:
                return Response({"code": 404,"message": "coin not found","data":None})
        else:
            return Response({"code":400,'message': 'coin_id is required.',"data":None})

        serializer = serializers.CoinDetailSerializer(coin)
        return Response({"code":200, "message":"ok", "data":serializer.data})
    
    def patch(self, request, address):
        try:
            coin = models.Coin.objects.get(address=address)
        except models.Coin.DoesNotExist:
            return Response({"code":400,'message': 'coin is not exist.',"data":None})
        serializer = serializers.CoinUpdateSerializer(instance=coin, data=request.data, partial=True)  
        if serializer.is_valid():
            if serializer.validated_data.get('status') == 0:
                coin.delete()
                return Response({"code":200, "message":"Delete successfully", "data":serializer.data})
            elif serializer.validated_data.get('status') == 1:
                serializer.save()
                return Response({"code": 200, "message": "ok", "data": serializer.data})
            else:
                return Response({"code": 400, "message": "status error", "data": None})
        return Response({"code": 400, "message": serializer.errors, "data": None})


class CoinCreateAPIView(APIView):
    authentication_classes = [JWTHeadersAuthentication,]
    def post(self, request):
        serializer = serializers.CoinCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.validated_data["creator_id"] = request.user.id
                coin = serializer.create_or_update(serializer.validated_data)
                data = serializers.CoinCreateSerializer(coin).data
                chain_id = coin.chain_id
                if not chain_id:
                    return Response({"code":400, "message":"chain_id is required","data":None})
                for chain, info in settings.CHAINLIST.items():
                    if info.get("id") == chain_id:
                        if "_" in info['name']:
                            logo_name = info['name'].split("_")[0]
                        else:
                            logo_name = info['name']
                        result = {
                            'id': info["id"], 
                            'name': info['name'], 
                            'logo': f'{settings.S3_BASE_URL}/chains/logo/'+logo_name+'.png',
                            'native': info['native'],
                            'explorer': info['explorer'],
                            'explorer_tx': info['explorer_tx']
                        }
                        data["chain"] = result
                return Response({"code": 200, 'message': 'ok', "data": data})
            except Exception as e:
                return Response({"code": 400, 'message': str(e), "data": None})
        return Response({"code": 400, 'message': serializer.errors, "data": None})
    
    def patch(self, request):
        serializer = serializers.CoinPatchSerializer(data=request.data,context={'request': request})
        if serializer.is_valid():
            data = serializer.validated_data
            hash = data.get('hash')
            wallet_address = data.get('wallet_address')
            chain_id = data.get('chain_id')
            token_address = data.get('address')
            totalSupply = data.get('total_supply')
            decimal = int(data.get('decimal'))
            price = float(data.get('initial_price',0))
            total_supply=Decimal(totalSupply) / Decimal(10**decimal)
            if not hash:
                return Response({"code":400,'message': 'hash is required',"data": None})
            try:
                coin = models.Coin.objects.get(hash=hash,chain_id=chain_id)
                coin.address = data["address"]
                coin.status = data["status"]
                coin.price = price
                coin.save()
                try:
                    models.CoinHoldInfo.objects.get(wallet_address=token_address,token_address=token_address)
                except models.CoinHoldInfo.DoesNotExist:
                    models.CoinHoldInfo.objects.create(wallet_address=token_address,token_address=token_address,hold_amount=total_supply)
                response_data = serializers.CoinDetailSerializer(coin).data
                cache.set('meme_hub:create_cache', response_data, timeout=300)
                return Response({"code":200,'message': 'ok',"data": response_data})
            except models.Coin.DoesNotExist:
                try:
                    user = user_models.User.objects.get(wallet_address=wallet_address)
                except user_models.User.DoesNotExist:
                    return Response({'code':404, 'error': 'User not found', "data":None})
                serializer.validated_data.pop('wallet_address', None)
                serializer.validated_data.pop('chain', None)
                serializer.validated_data.pop('total_supply', None)
                serializer.validated_data.pop('decimal', None)
                serializer.validated_data.pop('initial_price', None)
                serializer.validated_data['price'] = price
                coin = serializer.save(creator=user)
                try:
                    models.CoinHoldInfo.objects.get(wallet_address=token_address,token_address=token_address)
                except models.CoinHoldInfo.DoesNotExist:
                    models.CoinHoldInfo.objects.create(wallet_address=token_address,token_address=token_address,hold_amount=total_supply)
                response_data = serializers.CoinDetailSerializer(coin).data
                cache.set('meme_hub:create_cache', response_data, timeout=300)
                return Response({"code":200,'message': 'ok',"data": response_data})
        return Response({"code":400,'message': serializer.errors,"data": None})

    def perform_authentication(self, request):
        if request.method == 'PATCH':
            token = request.META.get('HTTP_TOKEN')
            print(token)
            if not token:
                raise MyAuthenticationFailed({
                    'code': 400,
                    'message': 'Authentication token is required',
                    'data': None
                })
            if token == settings.COIN_AUTHORIZATION:
                return None
            raise MyAuthenticationFailed({
                'code': 400,
                'message': 'Authentication token is expired',
                'data': None
            })
        else:
            super().perform_authentication(request)
   

class CoinSearchAPIView(APIView):
    
    def get(self, request, keyword):
        pass
            
class CommentListPagination(PageNumberPagination):
    page_size = settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = settings.MAX_PAGE_SIZE


class CommentAPIView(APIView):
    authentication_classes = [JWTHeadersAuthentication,]
    
    def get(self, request, address=None):
        
        if not address:
            return Response({"code": 400, 'message': 'address is required.', "data": None})
        try:
            coin = models.Coin.objects.get(address=address)
        except models.Coin.DoesNotExist:
            return Response({"code": 400, 'message': 'coin does not exist.', "data": None})
        
        queryset = models.Comment.objects.filter(coin_id=coin.id).order_by('-created_at')
        page = CommentListPagination()
        paginate_queryset = page.paginate_queryset(queryset, request, self)
        if paginate_queryset is not None:
            serializer = serializers.CommentSerializer(paginate_queryset, many=True, context={"request": request})
            paginated_response = page.get_paginated_response(serializer.data)
            paginated_data = paginated_response.data
            response_data = {"code": 200, "message": "ok", "data": paginated_data}
            return Response(response_data)
        
        serializer = serializers.CommentSerializer(queryset, many=True, context={"request": request})
        response_data = {"code": 200, "message": "ok", "data": serializer.data}
        return Response(response_data)

    def perform_authentication(self, request):
        if request.method == 'GET':
            token = request.META.get('HTTP_AUTHORIZATION')
            if token:
                try:
                    super().perform_authentication(request)
                except Exception as e:
                    request.user = AnonymousUser()
                    return None
            else:
                request.user = AnonymousUser()
                return None
        else:
            super().perform_authentication(request)


class CommentCreateView(generics.CreateAPIView):
    authentication_classes = [JWTHeadersAuthentication,]
    serializer_class = serializers.CommentCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # print(serializer.validated_data)
            related_comments = serializer.validated_data.get("related_comments",[])
            # print(related_comments)
            serializer.validated_data["related_comments"] = []
            # user = user_models.User.objects.get(id=3)
            # comment = serializer.save(user=user)
            comment = serializer.save(user=self.request.user)
            for related_comment in related_comments:
                related_comment.related_comments.add(comment)
                related_comment.save()
            data = serializers.CommentSerializer(comment).data
            return Response({"code":200,'message': 'ok',"data":data})
        return Response({"code":400,'message': serializer.errors,"data":None})


class LikeApiView(APIView):
    authentication_classes = [JWTHeadersAuthentication,]
    serializer_class = serializers.LikeSerializer
    
    def post(self, request, comment_id):
        try:
            comment = models.Comment.objects.get(id=comment_id)
        except models.Comment.DoesNotExist:
            return Response({"code":404,"message":"Comment not found","data":None})
        # user = user_models.User.objects.get(id=1)
        # like, created = models.Like.objects.get_or_create(user=user, comment=comment)
        like, created = models.Like.objects.get_or_create(user=request.user, comment=comment)
        print(like,created)
        if not created:
            return Response({"code":400,"message":"You have already liked this comment","data":None})
        try:
            comment = models.Comment.objects.get(id=comment_id) 
        except models.Comment.DoesNotExist:
            return Response({"code":400,"message":"Comment does not exist","data":None})
        data = serializers.CommentSerializer(comment,context={"request":request}).data
        return Response({"code":200,"message":"ok","data":data})
    
    def delete(self, request, comment_id):
        try:
            comment = models.Comment.objects.get(id=comment_id)
        except models.Comment.DoesNotExist:
            return Response({"code":404,"message":"Comment not found","data":None})
        try:
            models.Like.objects.get(user=request.user, comment=comment).delete()
        except models.Like.DoesNotExist:
            return Response({"code":400,"message":"You have not liked this comment","data":None})
        try:
            comment = models.Comment.objects.get(id=comment_id)
        except models.Comment.DoesNotExist:
            return Response({"code":400,"message":"Comment does not exist","data":None})
        data = serializers.CommentSerializer(comment,context={"request":request}).data
        return Response({"code":200,"message":"ok","data":data})
        
