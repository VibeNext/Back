import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing
import configs.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')

django_asgi_application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})