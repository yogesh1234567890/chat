from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]

# python manage.py runserver_plus --cert-file cert.pem --key-file key.pem 192.168.10.70:8000