from django.urls import path, include
from .views import *

urlpatterns = [
    path('users/', UserAPIView.as_view(), name='user-list-create'),
    path('users/<int:user_id>/', UserDetailAPIView.as_view(), name='user-detail-by-id'),
    path('users/<int:user_id>/followers/', FollowUserAPIView.as_view(), name='follow-user'),
]
