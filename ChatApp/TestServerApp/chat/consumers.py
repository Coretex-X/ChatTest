from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import json

#Сообщение для себя
class YourConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Принимаем соединение
        await self.accept()

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
    pass

#Для групавых чатов
class GroupChatConsumer(AsyncWebsocketConsumer):
    pass

#Для уведомлений 
class NotificationConsumer(AsyncWebsocketConsumer):
    pass