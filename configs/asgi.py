import os
print(">>> LOADING configs.asgi (ProtocolTypeRouter MODE)")  # ★ 콘솔에 반드시 보여야 함

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')

from django.core.asgi import get_asgi_application

django_asgi_application = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing
import configs.routing

application = ProtocolTypeRouter({
    "http": django_asgi_application,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})