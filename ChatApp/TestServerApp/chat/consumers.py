from channels.generic.websocket import AsyncWebsocketConsumer
from .models import UserData
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from .models import UserData 
import json
import redis
from asgiref.sync import sync_to_async

data_json = {
    "room":None,
    "user_id":None,
    "guest_id":None,
    "token":None
}

data_json_new_chat = {
    "room":None,
    "user_id":None,
    "guest_id":None,
    "token":None
}

#Кансумер для подключение клиента
class DataConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def check_access(self, user_id, guest_id, room_id):
        #1. Проверяем есть ли пользователь в UserData
        #2. Проверяем существует ли комната с этим user_id и guest_id
        #3. Проверяем совпадает ли room_id с комнатой из БД
        try:
            user_exists = UserData.objects.filter(
                user_id=str(user_id), 
                guest_id=str(guest_id), 
                room=str(room_id)
            ).exists()
            return user_exists
        except Exception as e:
            print(f"Error in check_access: {e}")
            return False
        
    @sync_to_async
    def check_room_exists(self, room_id):
        #Проверяет, существует ли комната в базе
        #Возвращает: True - существует, False - нет
        try:
            user_exists = UserData.objects.filter(room=str(room_id)).exists()
            return user_exists
        except Exception as e:
            print(f"Error in check_access: {e}")
            return False

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        room_chat = data["room"]
        id_user = data["user_id"]
        guest_id = data["guest_id"]
        status_chat = data["status_chat"]
        token = data["token"]

        if status_chat == "new_chat":
            room_exists = await self.check_room_exists(room_chat)
            if room_exists == True:
                await self.close(code=4001)
            elif room_exists == False:
                data_json_new_chat["room"] = room_chat
                data_json_new_chat["user_id"] = id_user
                data_json_new_chat["guest_id"] = guest_id
                data_json_new_chat["token"] = token
        elif status_chat == "existing_chat":
            has_access = await self.check_access(id_user, guest_id, room_chat)
            print(has_access)
            if has_access == True:
                data_json["room"] = room_chat
                data_json["user_id"] = id_user
                data_json["guest_id"] = guest_id
                data_json["token"] = token
            elif has_access == False:
                await self.close(code=4001)

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
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if data_json["room"] is None:  # Или все None
            await self.close()
            return
        token = data_json["token"]

        # Проверяем токен
        token = data_json["token"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        token_user = self.room_name

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        token_user = self.room_name

        if token != token_user:
            await self.close()
            return
        self.room_name = data_json["room"]

        data_json["room"] = None
        data_json["token"] = None
        data_json["user_id"] = None

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
        await self.send(text_data=json.dumps({"message": message}, ensure_ascii=False))


#Чат для создание новых контактов пользователей
class NewChatConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def add_chat(self, user_id, guest_id, room_id):
        try:
            # Создаем новую запись
            UserData.objects.create(
                user_id=str(user_id),
                guest_id=str(guest_id),
                room=str(room_id),
                count=2,  # начальное значение
                groups="default"  # или другая группа
            )
            return True
        
        except Exception as e:
            print(f"Error adding chat connection: {e}")
            return False

    async def connect(self):
        if data_json_new_chat["room"] is None:  # Или все None
            await self.close()
            return
        token = data_json_new_chat["token"]
        
        # Проверяем токен
        token = data_json_new_chat["token"]
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        token_user = self.room_name

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        token_user = self.room_name

        if token != token_user:
            await self.close()
            return
        self.room_name = data_json_new_chat["room"]
        

        await self.add_chat(
            data_json_new_chat["user_id"],    
            data_json_new_chat["guest_id"],
            data_json_new_chat["room"]
        )
        await self.add_chat( 
            data_json_new_chat["guest_id"],
            data_json_new_chat["user_id"],    
            data_json_new_chat["room"]
        )

        data_json_new_chat["room"] = None
        data_json_new_chat["token"] = None
        data_json_new_chat["user_id"] = None
       
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