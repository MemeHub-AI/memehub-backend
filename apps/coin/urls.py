from django.urls import path,include
from .views import *

urlpatterns = [
    path('coinslist/', CoinListView.as_view(), name='coin-list'),
    path('coins/<int:coin_id>/', CoinAPIView.as_view(), name='coin-detail'),
    path('coins/', CoinCreateAPIView.as_view(), name='coin-create'),
    path('comments/<int:coin_id>/', CommentAPIView.as_view(), name='comment-detail'),
    path('comments/', CommentCreateView.as_view(), name='comment-create'),
    path('like/<int:comment_id>/', LikeApiView.as_view(), name='like'),
]