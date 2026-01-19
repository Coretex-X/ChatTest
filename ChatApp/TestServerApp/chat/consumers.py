import json
from channels.generic.websocket import WebsocketConsumer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # Вызывается при подключении клиента
        self.accept()  # Принимаем соединение

    def disconnect(self, close_code):
        # Вызывается при отключении клиента
        pass  # Пока ничего не делаем

    def receive(self, text_data):
        # Вызывается при получении сообщения от клиента
        text_data_json = json.loads(text_data)  # Парсим JSON
        message = text_data_json["message"]  # Извлекаем текст сообщения
        
        # Отправляем обратно то же сообщение
        self.send(text_data=json.dumps({"message": message}))
        