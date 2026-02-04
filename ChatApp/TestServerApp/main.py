import requests as rq
import websocket
import json

'''json_reqistartion = {
    "login":"User5",
    "email":"user5@mail.ru",
    "number":"99999999999",
    "password":"12345678"
}
response = rq.post("http://127.0.0.1:5000/api/v2/user/registration/", json=json_reqistartion)'''


'''json_login = {
    "login":"User4",
    "password":"12345678"
}
response_login = rq.post("http://127.0.0.1:5000/api/v2/user/login/", json=json_login)

response_json = response_login.json()
id_user = response_json["id_users"]

sesion = {
    "id_users": id_user,
    "action": "offline"       
}
response_sesion = rq.post("http://127.0.0.1:5000/api/v2/user/sesion/", json=sesion)'''

'''rq.post("http://127.0.0.1:5000/chat/v2/user/get_user_data/", json={
    "user_room": "lobby",
    "user_id": 123
})'''

'''ws = websocket.WebSocket()

ws.connect("ws://127.0.0.1:5000/ws/data/")
ws.send(json.dumps({
    "room":"lobbi_7",
    "user_id":9,
    "guest_id":10,
    "status_chat":"existing_chat",
    "token":"api87"
})) #existing
ws.connect("ws://127.0.0.1:5000/ws/chat_user/api87/")
while True:
    message = str(input(": "))
    ws.send(json.dumps({"message": message}))
    print(ws.recv())  # {"message": "Hello"}'''

import redis

# Подключение к Redis (по умолчанию localhost:6379)
r = redis.Redis(
    host='localhost',
    port=6379,
    db=0,  # номер базы (0-15)
    decode_responses=True  # автоматически декодировать bytes в str
)

# Проверка подключения
try:
    r.ping()
    print("Успешно подключено к Redis!")
except redis.ConnectionError:
    print("Ошибка подключения к Redis")