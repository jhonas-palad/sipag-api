"""
ASGI config for sipag project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from .middlewares import JWTAuthMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sipag.settings")


from .ws_routes import ws_urlpatterns


def get_ws_handler():
    django.setup()
    return (AllowedHostsOriginValidator(JWTAuthMiddleware(URLRouter(ws_urlpatterns))),)


application = ProtocolTypeRouter(
    {"http": get_asgi_application(), "websocket": get_ws_handler()}
)
