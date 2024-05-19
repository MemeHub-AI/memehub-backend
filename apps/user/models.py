from typing import Any
from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.


class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)      
    logo = models.CharField(max_length=255,null=True,blank=True)
    description = models.CharField(max_length=255,null=True,blank=True)
    wallet_address = models.CharField(max_length=65,null=True,blank=True)
    followers = models.ManyToManyField('self', through='UserFollowers', symmetrical=False, related_name='following_users')
    sign = models.CharField(max_length=255,null=True,blank=True)
    chain_id = models.IntegerField(default=1, verbose_name='chainId')
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.name

    class Meta:
        db_table = 'user'
        constraints = [
            models.UniqueConstraint(fields=["id", "wallet_address", "chain_id"], name="unique_user")
        ]

class UserFollowers(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relationships')
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relationships')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.user == self.follower:
            raise ValidationError('You cannot follow yourself.')

        reverse_relationship = UserFollowers.objects.filter(user=self.follower, follower=self.user).exists()
        if reverse_relationship:
            raise ValidationError("This relationship already exists.")

    class Meta:
        db_table = 'followers'


class NewsArticle(models.Model):
    title = models.JSONField()
    image = models.JSONField()
    articles = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        db_table = 'news_article'
