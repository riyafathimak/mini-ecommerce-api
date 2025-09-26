from django.urls import path
from . import views
from user.views import UserViewSet
from django.contrib.auth.models import User
from django.urls import include, path
from rest_framework import routers, serializers, viewsets
from user.views import UserViewSet
from django.urls import path
from .views import LoginAPIView, LogoutAPIView, UserCreateAPIView,UserDeleteAPIView,UserListAPIView,UserUpdateAPIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Routers provide a way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/',LogoutAPIView.as_view(),name='logout'),
     path('user/', UserListAPIView.as_view(), name='user-list'),
    path('user/create/', UserCreateAPIView.as_view(), name='user-create'),
    path('user/<int:id>/update/', UserUpdateAPIView.as_view(), name='user-update'),
    path('user/<int:id>/delete/', UserDeleteAPIView.as_view(), name='user-delete'),
    # path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),


]