import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def sanitize_filename(url):
    # Удаляем запрещённые символы и оставляем только имя файла
    filename = re.sub(r'[\\/*?:"<>|]', "", url.split("/")[-1].split("?")[0])
    # Обрезаем до 50 символов и добавляем расширение .mp4
    return filename[:50] + ".mp4"

def download_video(url, save_folder="downloaded_videos"):
    try:
        os.makedirs(save_folder, exist_ok=True)
        filename = sanitize_filename(url)
        save_path = os.path.join(save_folder, filename)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        # Проверяем, является ли URL iframe (требует отдельной обработки)
        if "iframe" in url.lower():
            print(f"⚠️ Пропускаем iframe-ссылку: {url}")
            return

        with requests.get(url, headers=headers, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"✅ Видео сохранено: {save_path}")

    except Exception as e:
        print(f"❌ Ошибка при загрузке {url}: {type(e).__name__} — {e}")

# Пример использования
video_links = [
    "https://m.vpoisk.xyz/49633/"
]

for link in video_links:
    download_video(link)