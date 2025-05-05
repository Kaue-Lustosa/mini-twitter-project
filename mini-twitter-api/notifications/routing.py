from django.urls import re_path
from . import consumers
from .middleware import JWTAuthMiddleware
from channels.routing import URLRouter

websocket_urlpatterns = [
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]

# Apply JWT auth middleware
websocket_application = JWTAuthMiddleware(
    URLRouter(websocket_urlpatterns)
)
