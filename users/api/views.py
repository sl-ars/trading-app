from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from users.api.serializers import RegisterSerializer, LoginSerializer, UserSerializer

User = get_user_model()

### ==== DRF API Using ViewSet & Router ==== ###

class UserViewSet(viewsets.ViewSet):
    """
    User API using ViewSet:
    - `/api/users/register/` → Create a new user
    - `/api/users/login/` → Login and get JWT token
    - `/api/users/profile/` → Retrieve logged-in user's profile
    """

    @swagger_auto_schema(request_body=RegisterSerializer)
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """ API to register a new user """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "User registered successfully!"})

    @swagger_auto_schema(request_body=LoginSerializer)
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """ API to login and retrieve JWT token """
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        """ API to retrieve the authenticated user's profile """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
