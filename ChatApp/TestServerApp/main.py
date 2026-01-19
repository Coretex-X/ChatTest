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


ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:5000/ws/chat/lobby/")
ws.send(json.dumps({"message": "Hello"}))
print(ws.recv())  # {"message": "Hello"}