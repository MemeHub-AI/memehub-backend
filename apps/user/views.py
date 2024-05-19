import os
from django.conf import settings
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from . import models, utils, serializers
from extension.auth import JWTHeadersAuthentication
# Create your views here.
        

class UserAPIView(APIView):
    
    authentication_classes = [JWTHeadersAuthentication,]
    
    def get(self, request):
        try:
            serializer = serializers.UserDetailSerializer(request.user)
            return Response({"code":200, "message":"ok", "data":serializer.data})
        except Exception as e:
            return Response({"code":400, "message":"error", "data":None})
    
    def patch(self, request):
        serializer = serializers.UserSerializer(instance=request.user, data=request.data, partial=True)  
        if serializer.is_valid():
            serializer.save()
            return Response({"code": 200, "message": "Success", "data": None})
        return Response({"code": 400, "message": serializer.errors, "data": None})
    
    def post(self, request):
        serializer = serializers.UserAddSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            sign = data.get('sign','')
            try:
                user = models.User.objects.get(wallet_address=data['wallet_address'],chain_id=data['chain_id'])
            except models.User.DoesNotExist:
                user = serializer.save()
            except Exception as e:
                return Response({'code': 400, 'message': 'param error', 'data': None})
            if sign:
                token = utils.create_token({'sign':sign,'user_id':user.id,'wallet_address':user.wallet_address})
                user.sign = sign
                user.save()
                return Response({"code": 200, "message": "ok", "data": {"token": token.decode('utf-8')}})
            else:
                return Response({"code": 400, "message": "please input sign", "data": None})
        return Response({"code":400, "message": serializer.errors, "data":None})

class UserDetailAPIView(APIView):
    def get(self, request, user_id=None):
        if user_id:
            user = models.User.objects.get(id=user_id)
        else:
            return Response({"code":400,'message': 'User ID or wallet address is required.',"data":None})

        serializer = serializers.UserDetailSerializer(user)
        data = {key: value for key, value in serializer.data.items() if key not in ['replies', 'notifications']}
        return Response({"code":200, "message":"ok", "data": data})
    

class FollowUserAPIView(APIView):
    authentication_classes = [JWTHeadersAuthentication,]
    
    def post(self, request, user_id):
        if not request.user:
            return Response({"code":400,"message": "You must be logged in to perform this action.","data":None})
        user = get_object_or_404(models.User, id=user_id)
        follower = request.user  
        # follower = get_object_or_404(User, id=2)
        if user == follower:
            return Response({"code": 400, 'message': 'You cannot follow yourself.', "data": None})
        if models.UserFollowers.objects.filter(user=user, follower=follower).exists():
            return Response({"code": 400, 'message': 'You are already following this user.', "data": None})
        models.UserFollowers.objects.create(user=user, follower=follower)
        return Response({"code": 200, "message": "User followed successfully.", "data":None})

    def delete(self, request, user_id):
        if not request.user:
            return Response({"code":400,"message": "You must be logged in to perform this action.","data":None})
        # user = User.objects.get(id=user_id)
        user = get_object_or_404(models.User, id=user_id)
        follower = request.user 
        # follower = get_object_or_404(User, id=2)
        if not models.UserFollowers.objects.filter(user=user, follower=follower).exists():
            return Response({'code': 400,'message': 'You are not following this user.', 'data': None})
        models.UserFollowers.objects.filter(user=user, follower=follower).delete()
        return Response({'code': 200,'message': 'You have successfully unfollowed this user.', 'data': None})


class AvatarUploadView(APIView):
    # parser_classes = (MultiPartParser, FormParser)
    def post(self, request, *args, **kwargs):
        avatar_file = request.FILES.get('avatar')
        if not avatar_file:
            return Response({'code':400,'message': "Please upload a picture.", "data": None})
        file_type = os.path.splitext(avatar_file.name)
        if len(file_type) >= 2:
            new_name = file_type[0] + "-" + utils.get_random_str() + file_type[-1]
        else:
            new_name = avatar_file.name + "-" + utils.get_random_str()
        try:
            # print("a",new_name)
            result = utils.upload_image(new_name,avatar_file)
            # print("result",result)
            if result:
                image_url = "https://s3.ap-east-1.amazonaws.com/"+settings.BUCKET_NAME+"/"+new_name
                return Response({'code': 200,'message': 'ok', 'data': {"image_url":image_url}})
            return Response({"code":400, "message": "upload failed", "data": None})
        except Exception as e:
            return Response({"code":400, "message": e, "data": None})


class LatestNewsArticleListView(generics.ListAPIView):
    queryset = models.NewsArticle.objects.all().order_by('-create_time')[:30]
    serializer_class = serializers.NewsArticleSerializer