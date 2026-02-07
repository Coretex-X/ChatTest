from channels.generic.websocket import AsyncWebsocketConsumer
from .models import UserData
from sign_up.models import Models
import json
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool
from asgiref.sync import sync_to_async

redis_pool = ConnectionPool.from_url(
    'redis://localhost:6379/0',
    max_connections=100,
    decode_responses=True,
    socket_keepalive=True
)
redis_client = Redis(connection_pool=redis_pool)

session_id = {
    "token":None
}

#=============================================================================================================================================================================================
#Кансумер для подключение клиента
class DataConsumer(AsyncWebsocketConsumer):
    @sync_to_async
    def check_access(self, id_user, guest_id, room_chat, status_chat):
        try:
            if status_chat == "existing_chat":
                user_exists = UserData.objects.filter(
                    user_id=str(id_user), 
                    guest_id=str(guest_id), 
                    room=str(room_chat)
                ).exists()
                return user_exists
            elif status_chat == "new_chat":
                user_exists = UserData.objects.filter(room=str(room_chat)).exists()
                return user_exists
            
        except Exception as e:
            print(f"Error in check_access: {e}")
            return False
        
    @sync_to_async
    def id_session_user(id_user):
        user_token = Models.objects.filter(pk=id_user)
        id_session = user_token.token
        return id_session
        
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

        #id_session = await self.check_access(id_user=id_user)

        if status_chat == "new_chat":
            room_exists = await self.check_access(id_user=None, guest_id=None, room_chat=room_chat, status_chat="new_chat")
            if room_exists == True:
                await self.close(code=4001)
            elif room_exists == False:
                await redis_client.setex(f"session:new_chat:1234", 300, json.dumps({
                    "room":room_chat,
                    "user_id":id_user,
                    "guest_id":guest_id,
                    "token":token}))

        elif status_chat == "existing_chat":
            has_access = await self.check_access(id_user=id_user, guest_id=guest_id, room_chat=room_chat, status_chat="existing_chat")
            if has_access == True:
                await redis_client.setex(f"session:existing_chat:1234", 300, json.dumps({
                    "room":room_chat,
                    "user_id":id_user,
                    "guest_id":guest_id,
                    "token":token}))
            elif has_access == False:
                await self.close(code=4001)

            #wait redis_client.setex(f"session:usr_token:{token}", 300, json.dumps({"token":id_session}))
            #session_id["token"] = id_session

        await self.send(json.dumps({
            "action": "connect_to_chat",
        }))
        await self.close()


#=============================================================================================================================================================================================
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
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        #room_token = self.room_name
        #session_token = await redis_client.get(f"session:usr_token:{room_token}")
        #data_token = json.loads(session_token)
        #session_id = data_token["token"]
        # 1. Получаем данные из Redis по ключу, который был установлен при connect в DataConsumer
        session_data = await redis_client.get(f"session:existing_chat:1234")  # используем тот же ключ, что и при сохранении
        # 2. Если нет данных - закрываем
        if session_data is None:
            await self.close()
            return
        # 3. Разбираем JSON
        data = json.loads(session_data)
        token = data["token"]

        #Проверяем токен
        
        token_user = self.room_name
        if token != token_user:
            await self.close()
            return
        self.room_name = data["room"]


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


#==============================================================================================================================================================================================
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
        # 1. Получаем данные из Redis по ключу, который был установлен при connect в DataConsumer
        session_data = await redis_client.get("session:new_chat:1234")  # используем тот же ключ, что и при сохранении
        # 2. Если нет данных - закрываем
        if session_data is None:
            await self.close()
            return
        # 3. Разбираем JSON
        data = json.loads(session_data)
        token = data["token"]

        #Проверяем токен
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        token_user = self.room_name
        if token != token_user:
            await self.close()
            return
        self.room_name = data["room"]
        
        await self.add_chat(data["user_id"],data["guest_id"],data["room"])
        await self.add_chat(data["guest_id"],data["user_id"],data["room"])
       
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



#==============================================================================================================================================================================================
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