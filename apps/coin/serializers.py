from rest_framework import serializers
from apps.user.models import User
from apps.user.serializers import UserDetailSerializer
from django.contrib.auth.models import AnonymousUser
from .models import Coin, Comment, Like
from django.conf import settings


class CoinSerializer(serializers.ModelSerializer):
    creator = UserDetailSerializer(read_only=True)
    image = serializers.CharField(read_only=True)
    market_cap = serializers.FloatField(read_only=True)
    total_replies = serializers.IntegerField(source='replies', read_only=True)
    chain = serializers.SerializerMethodField()
    
    def get_chain(self, obj):
        chain_id = str(obj.chain_id)
        if chain_id:
            for chain, info in settings.CHAINLIST.items():
                if info.get("id") == chain_id:
                    logo_name = info['name']
                    if "_" in info['name']:
                        logo_name = info['name'].split("_")[0]
                    return {
                        'id': info["id"], 
                        'name': info['name'], 
                        'logo': f'{settings.S3_BASE_URL}/chains/logo/'+logo_name+'.png',
                        'native': info['native'],
                        'explorer': info['explorer'],
                        'explorer_tx': info['explorer_tx']
                    }
        return None
            
    
    def update(self, instance, validated_data):
        instance.hash = validated_data.get('hash', instance.hash)
        instance.market_cap = validated_data.get('market_cap', instance.market_cap)
        instance.virtual_liquidity = validated_data.get('virtual_liquidity', instance.virtual_liquidity)
        instance.status = validated_data.get('status', instance.status)
        instance.save()
        return instance
    
    class Meta:
        model = Coin
        fields = ['id', 'image', 'address', 'ticker', 'creator', 'name', 'desc', 'market_cap', 'total_replies',"chain"]

class CoinDetailSerializer(serializers.ModelSerializer):
    creator = UserDetailSerializer(read_only=True)
    class Meta:
        model = Coin
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        result = None
        chain_id = str(instance.chain_id)
        if chain_id:
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
                        'explorer_tx': info['explorer_tx'],
                    }
        representation['chain'] = result
        del representation['chain_id']
        return representation

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
    twitter_url = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    telegram_url = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    website = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    hash = serializers.CharField(required=True)
    chain = serializers.CharField(required=True)  
    # chain_info = serializers.SerializerMethodField(source='get_chain')  
    creator = serializers.SerializerMethodField()

    def validate(self, data):
        chain = data.get('chain')
        if chain:
            chain_info = settings.CHAINLIST.get(chain.lower())
            if chain_info is None:
                raise serializers.ValidationError("Invalid chain value")
            data['chain_id'] = chain_info["id"]  
            # data['chain_name'] = chain_info["name"]
        return data

    def get_creator(self, obj):
        user = User.objects.filter(id=obj.creator_id).first()
        return UserDetailSerializer(user).data

    def get_chain(self, obj):
        chain_id = str(obj.chain_id)
        if chain_id:
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
                        'explorer': info['explorer']
                    }
                    return result
        return None
    
    class Meta:
        model = Coin
        fields = ['name', 'address', 'chain', 'ticker', 'desc', 'image', 'twitter_url', 'telegram_url', 'website', 'hash', 'market_cap', 'virtual_liquidity', 'replies', 'status', 'create_time', 'creator']
        read_only_fields = ['market_cap', 'virtual_liquidity', 'replies', 'status', 'create_time']

    def create_or_update(self, validated_data):
        hash_value = validated_data.get('hash')
        chain_id = validated_data.get('chain_id')  
        del validated_data["chain"]
        try:
            existing_coin = Coin.objects.get(hash=hash_value, chain_id=chain_id)
            for attr, value in validated_data.items():
                setattr(existing_coin, attr, value)
            existing_coin.save()
            return existing_coin
        except Coin.DoesNotExist:
            return Coin.objects.create(**validated_data)

    
class CoinPatchSerializer(serializers.ModelSerializer):
    status = serializers.IntegerField(default=1)
    wallet_address = serializers.CharField(write_only=True)
    chain = serializers.CharField(write_only=True)  
    chain_id = serializers.IntegerField(read_only=True) 
    address = serializers.CharField(required=True)
    total_supply = serializers.CharField(required=False)
    decimal = serializers.IntegerField(required=True)
    initial_price = serializers.IntegerField(required=True)
    def validate(self, data):
        chain = data.get('chain')
        total_supply = data.get('total_supply')
        if chain:
            chain_id = settings.CHAINLIST.get(chain)
            if chain_id is None:
                raise serializers.ValidationError("Invalid chain value")
            data['chain_id'] = chain_id["id"]  
        if total_supply:
            data['total_supply'] = float(total_supply)
        return data
        
        
    class Meta:
        model = Coin
        fields = ['address', "chain_id", 'hash', "wallet_address", 'status', 'chain', 'total_supply', 'decimal', 'initial_price']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'comment', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    coin = CoinSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'coin', 'img', 'related_comments', 'created_at', 'likes_count', 'is_liked']
    
    def get_is_liked(self, obj):
        request = self.context.get('request', None)
        if request and isinstance(request.user, AnonymousUser):
            return False
        if request and request.user:
            return obj.likes.filter(user=request.user).exists()
        return False

class CommentCreateSerializer(serializers.ModelSerializer):
    related_comments = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(),
        many=True, allow_empty=True)
    coin = serializers.CharField()
    coin_detail = CoinSerializer(source='coin', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'coin','coin_detail', 'img', 'likes_count', 'created_at', 'related_comments']
        read_only_fields = ['id', 'likes_count', 'created_at']
        
    def create(self, validated_data):
        coin_address = validated_data.pop('coin')
        validated_data.pop('related_comments')
        coin = Coin.objects.get(address=coin_address)  
        comment = Comment.objects.create(coin=coin, **validated_data)
        return comment
