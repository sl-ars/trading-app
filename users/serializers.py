from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'avatar_url')

    def get_avatar_url(self, obj):
        if obj.avatar:
            return obj.avatar.url
        return None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, min_length=8, help_text="Password must be at least 8 characters long.")
    password2 = serializers.CharField(write_only=True, required=True, help_text="Confirm your password.")

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'role', 'phone_number')

    def validate(self, data):
        """ Validate that passwords match """
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def create(self, validated_data):
        """ Create a new user and return it """
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, help_text="Username of the user.")
    password = serializers.CharField(write_only=True, help_text="Password of the user.")

    def validate(self, data):
        from django.contrib.auth import authenticate
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError("Wrong credentials")

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user, context=self.context).data
        }


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number')


class AvatarUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avatar',)