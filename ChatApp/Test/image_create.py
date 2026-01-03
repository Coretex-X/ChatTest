import requests


url = "http://127.0.0.1:7000/api/v1/main/image-create/"
file_path = "/home/archlinux05/ChatApp/Z.png"

# ✅ Правильная отправка
with open(file_path, 'rb') as f:
    files = {'image': (file_path, f, 'image/jpeg')}
    response = requests.post(url, files=files)