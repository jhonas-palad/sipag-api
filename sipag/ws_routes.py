from django.urls import re_path
from channels.generic.websocket import WebsocketConsumer
from waste.urls import ws_urlpatterns as waste_ws_urlpatterns
import json


class PostConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send(
            text_data=json.dumps({"type": "make_connect", "message": "connected!"})
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))


ws_urlpatterns = [
    re_path(r"^ws$", PostConsumer.as_asgi()),
] + waste_ws_urlpatterns
