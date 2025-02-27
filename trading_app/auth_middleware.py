from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from channels.sessions import CookieMiddleware, SessionMiddleware
from django.contrib.sessions.models import Session
from rest_framework_simplejwt.tokens import AccessToken
import jwt
from django.conf import settings
from rest_framework_simplejwt.tokens import TokenError


def is_jwt_signature_valid(token_key):
    """ Checks if a JWT signature is valid using the secret key """
    try:
        jwt.decode(token_key, settings.SECRET_KEY, algorithms=["HS256"])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False



User = get_user_model()

class JWTSessionAuthMiddleware(BaseMiddleware):
    """ Custom WebSocket authentication middleware for JWT """

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode("utf-8")
        query_params = parse_qs(query_string)
        token_key = query_params.get("token", [None])[0]  # Get the JWT from query params

        scope["user"] = await self.get_user(token_key) if token_key else AnonymousUser()
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self, token_key):
        """ Validate JWT token and return the authenticated user """
        try:
            if not token_key:
                return AnonymousUser()

            access_token = AccessToken(token_key)
            if not is_jwt_signature_valid(token_key):
                return AnonymousUser()
            user = User.objects.get(id=access_token["user_id"])
            return user if user.is_active else AnonymousUser()

        except Exception:
            return AnonymousUser()