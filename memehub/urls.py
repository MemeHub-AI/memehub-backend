"""
URL configuration for memehub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from apps.user import views as user_views
from apps.resource.views import log_notify, ping

urlpatterns = [
    path('api/v1/user/', include('user.urls')),
    path('api/v1/coin/', include('coin.urls')),
    path('api/v1/upload/', user_views.AvatarUploadView.as_view()),
    path('api/v1/news/', user_views.LatestNewsArticleListView.as_view()),
    path('api/v1/log_notify/', log_notify),
    path('ping', ping)
]
