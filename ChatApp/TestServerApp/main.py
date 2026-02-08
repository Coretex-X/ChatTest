import requests as rq
import websocket
import redis
import asyncio
import json
import os
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

'''json_reqistartion = {
    "login":"User5",
    "email":"user5@mail.ru",
    "number":"99999999999",
    "password":"12345678"
}
response = rq.post("http://127.0.0.1:5000/api/v2/user/registration/", json=json_reqistartion)


json_login = {
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
response_sesion = rq.post("http://127.0.0.1:5000/api/v2/user/sesion/", json=sesion)

print(response_login)'''


ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:5000/ws/data/")
ws.send(json.dumps({
    "room":"lobbi_3",
    "user_id":8,
    "guest_id":9,
    "status_chat":"existing_chat",
    "token":"api87"
})) #existing
ws.connect("ws://127.0.0.1:5000/ws/chat_user/api87/")
while True:
    message = str(input(": "))
    ws.send(json.dumps({"message": message}))
    print(ws.recv())  # {"message": "Hello"}



'''import json

# ИМПОРТИРУЕМ СИНХРОННЫЙ REDIS, а не асинхронный!
from redis import Redis  # ← ВАЖНО: без .asyncio
from redis.connection import ConnectionPool

# 1. СОЗДАЕМ ПУЛ СОЕДИНЕНИЙ
pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True,  # Автоматически конвертируем bytes в str
    encoding='utf-8',
    max_connections=10,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)

# 2. СОЗДАЕМ КЛИЕНТ
redis = Redis(connection_pool=pool)

# 3. ПРОВЕРЯЕМ ПОДКЛЮЧЕНИЕ (синхронно, без await!)
try:
    is_connected = redis.ping()  # ← просто вызываем, без await
    print("is_connected:", is_connected)
    if is_connected:
        print("✅ Успешное подключение к Redis!")
    else:
        print("❌ Не удалось подключиться")         
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")

# 4. ЗАПИСЫВАЕМ ДАННЫЕ (синхронно)
try:
    user_data = {
        "name": "Иван",
        "email": "ivan@example.com",
        "balance": 1000.50,
    }
    
    # setex - синхронный метод
    result = redis.setex(
        "user:123",
        3600,  # Время жизни в секундах (1 час)
        json.dumps(user_data)  # Данные в JSON
    )
    print(f"📝 Данные записаны. Результат: {result}")
    
except Exception as e:
    print(f"❌ Ошибка записи: {e}")

# 5. ЧИТАЕМ ДАННЫЕ (синхронно)
try:
    # get - синхронный метод
    encrypted_data = redis.get("user:123")
    
    if encrypted_data:
        # Десериализуем JSON
        data = json.loads(encrypted_data)
        print()
        print(f"📖 Прочитано: {data}")
        print(f"👤 Имя пользователя: {data['name']}")
        print(f"💰 Баланс: {data['balance']}")
    else:
        print("⚠️ Данные не найдены или истек TTL")
            
except Exception as e:
    print(f"❌ Ошибка чтения: {e}")

# 6. ДОПОЛНИТЕЛЬНЫЕ ОПЕРАЦИИ (синхронно)
try:
    # Проверяем TTL (сколько секунд осталось жить ключу)
    ttl = redis.ttl("user:123")
    print(f"⏰ TTL ключа 'user:123': {ttl} секунд")
    
    # Увеличиваем счетчик (атомарно)
    redis.set("counter", 0)
    redis.incr("counter")  # увеличивает на 1
    redis.incrby("counter", 5)  # увеличивает на 5
    counter_value = redis.get("counter")
    print(f"🔢 Значение счетчика: {counter_value}")
    
    # Удаляем ключ
    deleted = redis.delete("user:123")
    print(f"🗑️ Удалено ключей: {deleted}")
    
except Exception as e:
    print(f"❌ Ошибка в дополнительных операциях: {e}")'''
