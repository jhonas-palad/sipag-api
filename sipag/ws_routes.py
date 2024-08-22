from django.urls import include, re_path

from channels.generic.websocket import WebsocketConsumer


class PostConsumer(WebsocketConsumer):
    def connect(self):
        print(self.scope)
        self.accept()


ws_urlpatterns = [
    re_path(r"^ws", PostConsumer.as_asgi()),
]
