import requests as rq
import websocket
import json
import time as t

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

ws = websocket.WebSocket()

ws.connect("ws://127.0.0.1:5000/ws/data/")
ws.send(json.dumps({
    "room":"lobbi",
    "user_id":12345,
    "token":"api87"
}))

t.sleep(2)

ws.connect("ws://127.0.0.1:5000/ws/chat_user/api87/")
while True:
    message = str(input(": "))
    ws.send(json.dumps({"message": message}))
    print(ws.recv())  # {"message": "Hello"}