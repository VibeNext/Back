from django.urls import re_path
from . import consumers

# solutionHistory id로 채팅방 접속
websocket_urlpatterns = [
    re_path(r'ws/solutions/(?P<history_id>[A-Za-z0-9_-]{21})/chat/$', 
           consumers.ChatConsumer.as_asgi()),

]