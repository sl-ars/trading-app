"""
ASGI config for trading_app project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_app.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from notifications.routing import websocket_urlpatterns
from trading_app.auth_middleware import JWTSessionAuthMiddleware
from channels.security.websocket import AllowedHostsOriginValidator




application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTSessionAuthMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})

