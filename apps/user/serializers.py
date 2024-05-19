from apps.coin import models as coin_models
from rest_framework import serializers
from django.utils import timezone
from . import models

class CoinSerializer(serializers.ModelSerializer):
    class Meta:
        model = coin_models.Coin
        fields = ['name', 'ticker', 'desc', 'image', 'replies']

class UserDetailSerializer(serializers.ModelSerializer):
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    coins_created = serializers.SerializerMethodField()
    # coins_hold = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    notifications = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    mention_count = serializers.SerializerMethodField()
    
    def get_followers(self, obj):
        followers = models.UserFollowers.objects.filter(user=obj)
        return [{'name': follower.follower.name, 'logo': follower.follower.logo, 'follower_count': follower.follower.followers.count()} for follower in followers]

    def get_following(self, obj):
        following = models.UserFollowers.objects.filter(follower=obj)
        return [{'name': followed_user.user.name, 'logo': followed_user.user.logo, 'follower_count': followed_user.user.followers.count()} for followed_user in following]
    
    def get_coins_created(self, obj):
        coins = coin_models.Coin.objects.filter(creator=obj)
        serializer = CoinSerializer(coins, many=True)
        creator_name = obj.name
        creator_logo = obj.logo
        return [{'creator_name': creator_name, 'creator_logo': creator_logo, 'name': coin["name"], 'image': coin["image"], 'desc': coin["desc"], 'ticker': coin["ticker"], 'replies': coin["replies"]} for coin in serializer.data] 

    def get_replies(self, obj):
        replies = coin_models.Comment.objects.filter(user=obj)
        return [{'created_at': reply.created_at, 'content': reply.content, 'user': reply.user.name, 'img': reply.img, 'id': reply.id} for reply in replies]
    
    def get_notifications(self, obj):
        replies = coin_models.Comment.objects.filter(user=obj)
        result = []
        for reply in replies:
            if reply.related_comments.all():
                for comment in reply.related_comments.all():
                    result.append({'content': comment.content, 'user': comment.user.name, 'img': comment.img, 'id': comment.id})
        return result
    
    def get_like_count(self, obj):
        replies = coin_models.Comment.objects.filter(user=obj)
        total = 0
        for reply in replies:
            total += reply.likes_count
        return total
    
    def get_mention_count(self, obj):
        replies = coin_models.Comment.objects.filter(user=obj)
        result = []
        for reply in replies:
            if reply.related_comments.all():
                for comment in reply.related_comments.all():
                    result.append(comment.id)
        return len(set(result))
        
    class Meta:
        model = models.User
        fields = ['id', 'name', 'logo','wallet_address', 'followers', 'following', 'like_count', 'mention_count','coins_created', 'replies', 'notifications']

class UserAddSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = models.User
        fields = ['name', 'logo','description','wallet_address', 'sign', 'chain_id']

class UserSerializer(serializers.ModelSerializer):
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.logo = validated_data.get('logo', instance.logo)
        instance.description = validated_data.get('description', instance.description)
        instance.update_time = timezone.now()
        instance.save()
        return instance
    
    class Meta:
        model = models.User
        fields = ['name', 'logo','description']

class UserFollowersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserFollowers
        fields = '__all__'


class NewsArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NewsArticle
        fields = ['title', 'image', 'articles', 'create_time']