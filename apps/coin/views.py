from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from . import models, serializers
from django.db.models import Q
from django.conf import settings
from extension.auth import JWTHeadersAuthentication

# Create your views here.

class CoinListPagination(PageNumberPagination):
    page_size = settings.PAGE_SIZE
    page_size_query_param = 'page_size'
    max_page_size = settings.MAX_PAGE_SIZE


class CoinListView(generics.ListAPIView):
    queryset = models.Coin.objects.all()
    serializer_class = serializers.CoinSerializer
    pagination_class = CoinListPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        token = self.request.query_params.get('token', None)
        queryset = queryset.filter(status=1)
        if token:
            token = token.lower()
            queryset = queryset.filter(
                Q(name__icontains=token) | Q(ticker__icontains=token) | Q(creator__name__icontains=token)
            )

        return queryset


class CoinAPIView(APIView):
    authentication_classes = [JWTHeadersAuthentication,]
    
    def get(self, request, coin_id=None):
        if coin_id:
            coin = models.Coin.objects.get(id=coin_id)
        else:
            return Response({"code":400,'message': 'coin_id is required.',"data":None})

        serializer = serializers.CoinDetailSerializer(coin)
        return Response({"code":200, "message":"ok", "data":serializer.data})
    
    def patch(self, request, coin_id):
        try:
            coin = models.Coin.objects.get(id=coin_id)
        except models.Coin.DoesNotExist:
            return Response({"code":400,'message': 'coin is not exist.',"data":None})
        serializer = serializers.CoinUpdateSerializer(instance=coin, data=request.data, partial=True)  
        if serializer.is_valid():
            if serializer.validated_data.get('status') == 0:
                coin.delete()
                return Response({"code":200, "message":"Delete successfully", "data":None})
            elif serializer.validated_data.get('status') == 1:
                serializer.save()
                return Response({"code": 200, "message": "ok", "data": None})
            else:
                return Response({"code": 400, "message": "status error", "data": None})
        return Response({"code": 400, "message": serializer.errors, "data": None})


class CoinCreateAPIView(APIView):
    authentication_classes = [JWTHeadersAuthentication,]
    def post(self, request):
        serializer = serializers.CoinCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                coin = models.Coin.objects.get(name=data['name'],ticker=data['ticker'])
                if coin:
                    return Response({'code': 400, 'message': 'token is already exists', 'data': None})
            except models.Coin.DoesNotExist:
                coin = serializer.save(creator=self.request.user)
                return Response({"code":200,'message': 'ok',"data":{"coin_id":coin.id}})
        return Response({"code":400,'message': serializer.errors,"data":None})


class CommentAPIView(APIView):
    serializer_class =  serializers.CommentSerializer
    
    def get(self, request, coin_id=None):
        if not coin_id:
            return Response({"code":400,'message': 'coin_id is required.',"data":None})
        queryset = models.Comment.objects.filter(coin_id=coin_id)
        serializer = serializers.CommentSerializer(queryset, many=True)
        return Response({"code":200,'message': 'ok',"data":serializer.data})


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
            # user = models.User.objects.get(id=3)
            # comment = serializer.save(user=user)
            comment = serializer.save(user=self.request.user)
            for related_comment in related_comments:
                related_comment.related_comments.add(comment)
                related_comment.save()
            return Response({"code":200,'message': 'ok',"data":None})
        return Response({"code":400,'message': serializer.errors,"data":None})


class LikeApiView(APIView):
    authentication_classes = [JWTHeadersAuthentication,]
    serializer_class = serializers.LikeSerializer
    
    def post(self, request, comment_id):
        try:
            comment = models.Comment.objects.get(id=comment_id)
        except models.Comment.DoesNotExist:
            return Response({"code":404,"message":"Comment not found","data":None})
        # user = models.User.objects.get(id=1)
        # like, created = models.Like.objects.get_or_create(user=user, comment=comment)
        like, created = models.Like.objects.get_or_create(user=request.user, comment=comment)
        if not created:
            return Response({"code":400,"message":"You have already liked this comment","data":None})
        return Response({"code":200,"message":"ok","data":None})
    
    def delete(self, request, comment_id):
        try:
            comment = models.Comment.objects.get(id=comment_id)
        except models.Comment.DoesNotExist:
            return Response({"code":404,"message":"Comment not found","data":None})
        try:
            # user = models.User.objects.get(id=1)
            # like = models.Like.objects.get(user=user, comment=comment)
            models.Like.objects.get(user=request.user, comment=comment).delete()
        except models.Like.DoesNotExist:
            return Response({"code":400,"message":"You have not liked this comment","data":None})
        return Response({"code":200,"message":"ok","data":None})
