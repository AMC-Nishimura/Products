"""
ASGI config for Products project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Products.settings')
django.setup()

from channels.auth import AuthMiddlewareStack
from django.urls import path, include
import tabjudge.routing


#application = get_asgi_application()

#Websocket 


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    # Just HTTP for now. (We can add other protocols later.)

    #ここでWebSocketサーバーのルーティングを登録( ws/chat/(?P<room_name>\w+)/ でconsumerを呼び出す )
    "websocket": AuthMiddlewareStack(
        URLRouter([
            #chat.routing.websocket_urlpatterns +
            #wss.routing.websocket_urlpatterns
            #path('', URLRouter(chat.routing.websocket_urlpatterns)),
            #path('', URLRouter(upload.routing.websocket_urlpatterns)),
            path('', URLRouter(tabjudge.routing.websocket_urlpatterns)),
        ])
    ),
})


