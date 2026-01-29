from channels.generic.websocket import AsyncWebsocketConsumer
from .models import UserData
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
import json
import redis
from asgiref.sync import sync_to_async

'''data_json = {
    "room":None,
    "user_id":None,
    "token":None
}'''
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)


#Кансумер для подключение клиента

class DataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        room_chat = data["room"]
        id_user = data["user_id"]
        token = data["token"]
        #data_json["room"] = room_chat
        #data_json["user_id"] = id_user
        #data_json["token"] = token

        # Записываем в Redis вместо глобального словаря
        await sync_to_async(redis_client.setex)(
            f"ws_data:{self.channel_name}",  # Ключ с channel_name
            30,  # 30 секунд TTL
            json.dumps({
                "room": room_chat,
                "user_id": id_user,
                "token": token
            })
        )
        
        await self.send(json.dumps({
            "action": "connect_to_chat",
        }))
        await self.close()


#Сообщение для себя
class YourConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print(self.channel_name)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        await self.send(text_data=json.dumps({
            "message": message,
        }))


#Для личных чатов пользователей (не мене 2 участников)
class PrivateChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        #if data_json["room"] is None:  # Или все None
        #    await self.close()
        #    return
        #token = data_json["token"]
        # Получаем channel из query
        query_string = self.scope['query_string'].decode('utf-8')
        channel_name = None
        if '=' in query_string:
            channel_name = query_string.split('=')[1]
        
        if not channel_name:
            await self.close()
            return
        
        # 1. ЧИТАЕМ из Redis
        data_json = await sync_to_async(redis_client.get)(f"ws_data:{channel_name}")
        
        # Проверяем что данные есть (аналог if data_json["room"] is None)
        if not data_json:
            await self.close()
            return
        
        data = json.loads(data_json)
        
        # Проверяем токен
        token = data["token"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        token_user = self.room_name

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        token_user = self.room_name

        if token != token_user:
            await self.close()
            return
        self.room_name = data["room"]
        #self.room_name = data_json["room"]

        #data_json["room"] = None
        #data_json["token"] = None
        #data_json["user_id"] = None
        await sync_to_async(redis_client.delete)(f"ws_data:{channel_name}")
        
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        #await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        pass

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))


#Для групавых чатов
class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message}
        )

    async def chat_message(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))


#Для уведомлений 
class NotificationConsumer(AsyncWebsocketConsumer):
    pass