# upload/routing.py
from django.urls import re_path

from . import consumers
from . import AsyncConsumers
#from . import targetConsumers

# WebSocketConsumerは.as_asgi()で呼び出せる。
websocket_urlpatterns = [
    #re_path(r'ws/upload/room/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
    #re_path(r'ws/upload/target/$', targetConsumers.ChatConsumer.as_asgi())
    re_path(r'ws/upload/$', consumers.UploadConsumer.as_asgi()),
    re_path(r'ws/asyncupload/$', AsyncConsumers.UploadConsumer.as_asgi())
]
