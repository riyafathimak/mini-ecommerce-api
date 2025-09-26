from django.shortcuts import render
from rest_framework import viewsets, filters
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import UserSerializer
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework import generics
from django.contrib.auth import authenticate
from rest_framework.response import Response 
from rest_framework.authtoken.models import Token



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['username', 'email']
    search_fields = ['username', 'email']
    ordering_fields = ['username', 'email']

class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user)
            return Response({
                "token": token.key,
                "user": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # only logged-in users

    def post(self, request):
        try:
            # Delete the token of the current user
            request.user.auth_token.delete()
        except (AttributeError, Token.DoesNotExist):
            return Response({"error": "Invalid token or already logged out"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "Successfully logged out"}, 
                        status=status.HTTP_200_OK)
class UserListAPIView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
class UserUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'   # or 'pk'

class UserDeleteAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'   # or 'pk'

    

