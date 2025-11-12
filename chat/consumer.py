from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(WebsocketConsumer):
    # 최초 연결
    def connect(self):
        self.accept()
    
    # 연결 종료        
    def disconnect(self, close_code):
        pass
    
    # 메세지 전송
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        self.send(text_data = json.dumps({
            'message': message
        }))