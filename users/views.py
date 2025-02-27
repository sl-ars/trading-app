from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from users.serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    ProfileUpdateSerializer,
    AvatarUpdateSerializer
)
from rest_framework.parsers import MultiPartParser
from django.contrib.auth import get_user_model

User = get_user_model()


class UserViewSet(viewsets.ViewSet):
    """
    User API using ViewSet:
    - `/api/users/register/` → Create a new user
    - `/api/users/login/` → Login and get JWT token
    - `/api/users/profile/` → Retrieve logged-in user's profile
    - `/api/users/profile/update/` → Update profile details (name, phone)
    - `/api/users/profile/avatar/` → Upload avatar
    """

    @swagger_auto_schema(request_body=RegisterSerializer, responses={201: UserSerializer})
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        if request.data.role not in ['customer', 'trader']:
            return Response({"error": "Permission denied!"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        return Response(UserSerializer(user, context={"request": request}).data)

    @swagger_auto_schema(request_body=LoginSerializer, responses={200: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='JWT Refresh Token'),
            'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT Access Token'),
            'user': openapi.Schema(type=openapi.TYPE_OBJECT, description='User Details', properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email'),
                'role': openapi.Schema(type=openapi.TYPE_STRING, description='User Role'),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone Number'),
                'avatar_url': openapi.Schema(type=openapi.TYPE_STRING, description='Avatar URL'),
            }),
        }
    )})
    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

    @swagger_auto_schema(responses={200: UserSerializer})
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def profile(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(serializer.data)

    @swagger_auto_schema(request_body=ProfileUpdateSerializer, responses={200: UserSerializer})
    @action(detail=False, methods=['patch'], permission_classes=[permissions.IsAuthenticated], url_path="profile/update")
    def profile_update(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user, context={"request": request}).data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="avatar",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Profile image file"
            )
        ],
        consumes=["multipart/form-data"],
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "avatar_url": openapi.Schema(type=openapi.TYPE_STRING, description="New avatar URL")
            }
        )}
    )
    @action(parser_classes=[MultiPartParser], detail=False, methods=['patch'], permission_classes=[permissions.IsAuthenticated],
            url_path="profile/avatar")
    def profile_avatar(self, request):
        """ Upload or update user avatar """
        serializer = AvatarUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"avatar_url": user.avatar.url})