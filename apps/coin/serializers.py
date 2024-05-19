from rest_framework import serializers
from apps.user.models import User
from .models import Coin, Comment, Like

class CoinSerializer(serializers.ModelSerializer):
    creator_logo = serializers.CharField(source='creator.logo', read_only=True)
    creator_name = serializers.CharField(source='creator.name', read_only=True)
    image = serializers.CharField(read_only=True)
    market_cap = serializers.FloatField(read_only=True)
    total_replies = serializers.IntegerField(source='replies', read_only=True)

    def update(self, instance, validated_data):
        instance.hash = validated_data.get('hash', instance.hash)
        instance.market_cap = validated_data.get('market_cap', instance.market_cap)
        instance.virtual_liquidity = validated_data.get('virtual_liquidity', instance.virtual_liquidity)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance

    class Meta:
        model = Coin
        fields = ['id', 'image', 'address', 'ticker', 'creator_logo', 'creator_name', 'name', 'desc', 'market_cap', 'total_replies']

class CoinDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Coin
        fields = '__all__'

class CoinUpdateSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        instance.hash = validated_data.get('hash', instance.hash)
        instance.address = validated_data.get('address', instance.address)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
        
    class Meta:
        model = Coin
        fields = ["address", 'hash', 'status']

class CoinCreateSerializer(serializers.ModelSerializer):
    twitter_url = serializers.CharField(allow_null=True,allow_blank=True)
    telegram_url = serializers.CharField(allow_null=True,allow_blank=True)
    website = serializers.CharField(allow_null=True,allow_blank=True)
    
    class Meta:
        model = Coin
        fields = ['name', 'chain_id', 'ticker', 'desc', 'image', 'twitter_url', 'telegram_url', 'website']
        read_only_fields = ['market_cap', 'virtual_liquidity', 'replies', 'status', 'create_time']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'logo']  

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'comment', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'coin', 'img', 'related_comments', 'created_at', 'likes_count']

class CommentCreateSerializer(serializers.ModelSerializer):
    related_comments = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(),
        many=True, allow_empty=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'coin', 'img', 'likes_count', 'created_at', 'related_comments']
        read_only_fields = ['id', 'likes_count', 'created_at']
