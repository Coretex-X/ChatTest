from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.core.cache import cache
from asgiref.sync import sync_to_async


#Сообщение для себя
class YourConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Принимаем соединение
        await self.accept()
        print(self.channel_name)

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        # Получаем и отправляем обратно (эхо)
        try:
            data = json.loads(text_data)
            message = data["message"]
            
            # Просто возвращаем сообщение обратно
            await self.send(text_data=json.dumps({
                "message": message,
            }))

            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "error": "Невалидный JSON"
            }))
        except KeyError:
            await self.send(text_data=json.dumps({
                "error": "Нет поля 'message' в JSON"
            }))


#Для личных чатов пользователей (не мене 2 участников)
class PrivateChatConsumer(AsyncWebsocketConsumer):
    '''async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)'''
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        
        MAX_USERS = 2
        cache_key = f"room_users_{self.room_name}"
        
        # Получаем текущее количество пользователей
        current_users = cache.get(cache_key, 0)
        
        if current_users >= MAX_USERS:
            await self.accept()
            await self.send(text_data=json.dumps({
                'error': 'Комната заполнена'
            }))
            await self.close()
            return
        
        # Увеличиваем счетчик
        cache.set(cache_key, current_users + 1, timeout=None)
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        cache_key = f"room_users_{self.room_name}"
        current_users = cache.get(cache_key, 0)
        
        # Уменьшаем счетчик при отключении
        if current_users > 0:
            cache.set(cache_key, current_users - 1, timeout=None)
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    

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
    pass

#Для уведомлений 
class NotificationConsumer(AsyncWebsocketConsumer):
    pass