from django.db import models
from django.conf import settings
from apps.user import models as user_models

# Create your models here.

class Coin(models.Model):
    creator = models.ForeignKey(user_models.User, on_delete=models.CASCADE, related_name='coin_creator')
    address = models.CharField(max_length=150, verbose_name="address")
    name = models.CharField(max_length=255, verbose_name='name')
    ticker = models.CharField(max_length=255,  verbose_name='ticker')
    desc = models.CharField(max_length=255, verbose_name='desc')
    image = models.CharField(max_length=255, verbose_name='logo')
    twitter_url = models.CharField(max_length=255, blank=True, null=True, verbose_name='twitterUrl')
    telegram_url = models.CharField(max_length=255, blank=True, null=True, verbose_name='telegramUrl')
    website = models.CharField(max_length=255, blank=True, null=True, verbose_name='websiteUrl')
    market_cap =  models.FloatField(blank=True, null=True, default=0, verbose_name='marketCap')
    virtual_liquidity = models.BigIntegerField(blank=True, null=True, default=0, verbose_name='virtualLiquidity')
    chain_id = models.IntegerField(default=1, verbose_name='chainId')
    price = models.FloatField(blank=True, null=True, default=0, verbose_name='price')
    replies = models.BigIntegerField(default=0)

    hash = models.CharField(max_length=255, blank=True, null=True, verbose_name="hash")
    status = models.IntegerField(default=2, verbose_name="status")

    create_time = models.DateTimeField(auto_now_add=True)

    @property
    def chain(self):
        return settings.CHAINID_MAPPING.get(self.chain_id, 'eth')

    class Meta:
        db_table = 'coin'

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    user = models.ForeignKey(user_models.User, on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, on_delete=models.CASCADE, related_name='comments')
    img = models.CharField(max_length=255, blank=True, null=True, verbose_name="img")
    related_comments = models.ManyToManyField('self', symmetrical=False, related_name='related_to')
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.coin.replies += 1
        self.coin.save()

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'comment'

class Like(models.Model):
    user = models.ForeignKey(user_models.User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.comment.likes_count += 1
        self.comment.save()

    def delete(self, *args, **kwargs):
        self.comment.likes_count -= 1
        self.comment.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Like by {self.user} on {self.comment}"

    class Meta:
        db_table = 'like'
        unique_together = ('user', 'comment')  
        constraints = [
            models.UniqueConstraint(fields=['user', 'comment'],  name='unique_like')
        ]
