import flet as ft
import datetime
import os
import shutil
import json
import time
import base64
import websocket
import threading
import queue

# ===============================================
# ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ДЛЯ ДАННЫХ ПОЛЬЗОВАТЕЛЕЙ
# ===============================================
# Данные текущего пользователя (кто использует приложение)
# ============================================================
# НАСТРОЙКА АВАТАРОВ - УКАЖИ ПУТЬ К ФОТО ЗДЕСЬ!
# ============================================================
# Чтобы использовать реальные фото вместо букв:
# 1. Укажи путь к своему фото в CURRENT_USER['avatar_path']
# 2. Укажи путь к фото собеседника в CONTACT_USER['avatar_path']
# Пример: "/home/user/photos/my_photo.jpg"
# ============================================================

# Папка для входящих файлов
INCOMING_FILES_FOLDER = "incoming_files1"
if not os.path.exists(INCOMING_FILES_FOLDER):
    os.makedirs(INCOMING_FILES_FOLDER)

id_user = 3
guest_id = 4

CURRENT_USER = {
    "id": id_user,
    "name": "Я",  # ← Измени свое имя тут
    "avatar_color": ft.Colors.BLUE,
    "phone": "+7 900 123-45-67",
    "status": "В сети",
    "about": "Это я"
}

# Данные собеседника (с кем переписываемся)
CONTACT_USER = {
    "id": guest_id,
    "name": "Друг",  # ← Измени имя собеседника тут
    "avatar_color": ft.Colors.GREEN,
    "phone": "+7 900 111-22-33",
    "status": "В сети",
    "about": "Мой друг",
    "last_seen": "только что"
}

# Настройки чата
CHAT_CONFIG = {
    "room_id": "lobbi_1",
    "theme": "light",
    "notifications": True
}


# ===============================================
# WEBSOCKET КЛИЕНТ - ПОЛУЧЕНИЕ СООБЩЕНИЙ ОТ СОБЕСЕДНИКА
# ===============================================


message_queue = queue.Queue()
ws = None
running = True

# 1. Аутентификация
def authenticate():
    ws_auth = websocket.WebSocket()
    ws_auth.connect("ws://127.0.0.1:5000/ws/data/")
    ws_auth.send(json.dumps({
        "room": "lobbi_1",
        "user_id": id_user,
        "guest_id": guest_id,
        "status_chat": "existing_chat",
        "token": "api87"
    }))
    ws_auth.close()

# Выполняем аутентификацию
authenticate()

# 2. Подключаемся к чату
ws = websocket.WebSocket()
ws.connect("ws://127.0.0.1:5000/ws/chat_user/api87/")

def receive_messages():
    """Получает сообщения от WebSocket и кладет их в очередь"""
    global running
    while running:
        try:
            # Пытаемся получить сообщение (может быть текст или бинарные данные)
            message = ws.recv()
            
            # Пробуем распарсить как JSON (текстовое сообщение)
            try:
                message_data = json.loads(message)
                print(f"📨 Получено текстовое сообщение: sender={message_data.get('sender_id')}, text={message_data.get('message')}")
                message_queue.put(message_data)
            except:
                # Если не JSON, значит это бинарные данные (файл)
                print(f"📦 Получены бинарные данные, размер: {len(message)} байт")
                
                # Ищем разделитель между метаданными и файлом
                separator = b"|||BINARY_DATA|||"
                separator_index = message.find(separator)
                
                if separator_index != -1:
                    # Отделяем метаданные от файла
                    metadata_bytes = message[:separator_index]
                    file_data = message[separator_index + len(separator):]
                    
                    # Парсим метаданные
                    metadata = json.loads(metadata_bytes.decode('utf-8'))
                    
                    print(f"📦 Метаданные файла: {metadata}")
                    
                    # Создаем сообщение для очереди
                    file_message = {
                        "type": "file",
                        "file_name": metadata.get("file_name", "unknown"),
                        "file_type": metadata.get("file_type", "unknown"),
                        "file_size": metadata.get("file_size", len(file_data)),
                        "file_data": base64.b64encode(file_data).decode('utf-8'),  # Кодируем в base64 для очереди
                        "sender_id": metadata.get("sender_id", None)
                    }
                    
                    message_queue.put(file_message)
                else:
                    print("❌ Не удалось найти разделитель в бинарных данных")
        
        except websocket.WebSocketConnectionClosedException:
            print("⚠️ WebSocket соединение закрыто")
            break
        except Exception as e:
            print(f"❌ Ошибка в receive_messages: {e}")
            import traceback
            traceback.print_exc()
            break

# Запускаем поток для прослушивания
thread = threading.Thread(target=receive_messages, daemon=True)
thread.start()

def main(page: ft.Page):
    page.title = "WhatsApp-like Chat"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    
    # Переменные состояния
    messages_column = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
    all_messages = []  # Список всех сообщений для возможности удаления
    sent_media_files = []  # Список отправленных медиа файлов (ТОЛЬКО через FilePicker, НЕ голосовые)
    viewed_one_time_messages = []  # Список просмотренных одноразовых сообщений
    
    # Объявляем переменные для кнопок заранее
    mic_button = None
    send_button = None
    attach_button = None
    
    # Папка для автосохранения файлов
    settings_file = "chat_settings.json"
    auto_download_folder = None
    
    # Для записи голосовых сообщений
    voice_recordings_folder = "voice_recordings"
    if not os.path.exists(voice_recordings_folder):
        os.makedirs(voice_recordings_folder)
    
    # Загрузка настроек
    def load_settings():
        nonlocal auto_download_folder
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    auto_download_folder = settings.get('auto_download_folder')
        except:
            pass
    
    # Сохранение настроек
    def save_settings():
        try:
            settings = {'auto_download_folder': auto_download_folder}
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False)
        except:
            pass
    
    load_settings()
    
    # ===============================================
    # ФУНКЦИИ ДЛЯ РАБОТЫ С АВАТАРКАМИ
    # ===============================================
    
    def create_avatar_widget(user_data, size=40, is_circle=True):
        """
        ПРОСТОЙ круг с первой буквой имени - БЕЗ ФОТО!
        """
        # Берем первую букву имени
        name = user_data.get("name", "?")
        letter = name[0].upper() if name else "?"
        
        # Просто круг с буквой
        return ft.CircleAvatar(
            content=ft.Text(letter, size=size//2),
            bgcolor=user_data.get("avatar_color", ft.Colors.GREY),
            radius=size//2,
        )
    
    
    
    # ===============================================
    # ОСТАЛЬНЫЕ ФУНКЦИИ (auto_save_file, download_file и т.д.)
    # ===============================================
    
    # Функция для автоматического сохранения файла
    def auto_save_file(file_path, file_name):
        if auto_download_folder and os.path.exists(auto_download_folder):
            try:
                dest_path = os.path.join(auto_download_folder, file_name)
                # Если файл уже существует, добавляем номер
                counter = 1
                while os.path.exists(dest_path):
                    name, ext = os.path.splitext(file_name)
                    dest_path = os.path.join(auto_download_folder, f"{name}_{counter}{ext}")
                    counter += 1
                
                shutil.copy2(file_path, dest_path)
                return dest_path
            except Exception as e:
                print(f"Ошибка автосохранения: {e}")
        return file_path
    
    # Диалог выбора папки для автосохранения
    def show_download_folder_dialog(e):
        def folder_picked(e: ft.FilePickerResultEvent):
            nonlocal auto_download_folder
            if e.path:
                auto_download_folder = e.path
                save_settings()
                page.open(
                    ft.SnackBar(content=ft.Text(f"Папка для сохранения: {auto_download_folder}"))
                )
                page.update()
        
        folder_picker = ft.FilePicker(on_result=folder_picked)
        page.overlay.append(folder_picker)
        page.update()
        folder_picker.get_directory_path(dialog_title="Выберите папку для автосохранения файлов")
    
    # Функция для скачивания файла вручную
    def download_file(file_path, file_name):
        try:
            def save_file_result(e: ft.FilePickerResultEvent):
                if e.path:
                    try:
                        shutil.copy2(file_path, e.path)
                        page.open(
                            ft.SnackBar(content=ft.Text(f"Файл сохранен: {e.path}"))
                        )
                        page.update()
                    except Exception as ex:
                        page.open(
                            ft.SnackBar(content=ft.Text(f"Ошибка сохранения: {str(ex)}"))
                        )
                        page.update()
            
            save_picker = ft.FilePicker(on_result=save_file_result)
            page.overlay.append(save_picker)
            page.update()
            
            save_picker.save_file(
                file_name=file_name,
                dialog_title="Сохранить файл как"
            )
        except Exception as e:
            page.open(
                ft.SnackBar(content=ft.Text(f"Ошибка: {str(e)}"))
            )
            page.update()
    
    # Функция для открытия изображения в полном размере
    def open_image_fullscreen(image_path, file_name):
        def close_dialog(e):
            page.close(image_dialog)
        
        def download_action(e):
            download_file(image_path, file_name)
        
        image_dialog = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Image(
                            src=image_path,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        ft.Text(file_name, size=14, weight=ft.FontWeight.BOLD),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=600,
                height=650,
            ),
            actions=[
                ft.TextButton("📥 Скачать", on_click=download_action),
                ft.TextButton("Закрыть", on_click=close_dialog),
            ],
        )
        page.open(image_dialog)
    
    # Функция для открытия видео
    def open_video_viewer(video_path, file_name):
        def close_dialog(e):
            page.close(video_dialog)
        
        def download_action(e):
            download_file(video_path, file_name)
        
        video_dialog = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Video(
                            playlist=[ft.VideoMedia(video_path)],
                            width=600,
                            height=400,
                            show_controls=True,
                        ),
                        ft.Text(file_name, size=14, weight=ft.FontWeight.BOLD),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                width=600,
            ),
            actions=[
                ft.TextButton("📥 Скачать", on_click=download_action),
                ft.TextButton("Закрыть", on_click=close_dialog),
            ],
        )
        page.open(video_dialog)
    
    # Диалог переименования файла
    def show_rename_dialog(file_info):
        file_path, original_name = file_info['path'], file_info['name']
        file_ext = os.path.splitext(original_name)[1]
        file_name_without_ext = os.path.splitext(original_name)[0]
        
        # Проверяем, это медиа файл?
        is_media = file_ext.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.mp4', '.avi', '.mov', '.mkv', '.webm', '.mp3', '.wav', '.ogg', '.m4a']
        
        rename_field = ft.TextField(
            value=file_name_without_ext,
            label="Название",
            expand=True,
            text_size=13,
        )
        
        one_time_checkbox = ft.Checkbox(
            label="Одноразовый",
            value=False,
        )
        
        def confirm_rename(e):
            new_name = rename_field.value.strip() + file_ext
            if new_name:
                file_info['display_name'] = new_name
            file_info['one_time_view'] = one_time_checkbox.value if is_media else False
            page.close(rename_dialog)
            add_file_to_chat(file_info)
        
        def skip_rename(e):
            file_info['display_name'] = original_name
            file_info['one_time_view'] = one_time_checkbox.value if is_media else False
            page.close(rename_dialog)
            add_file_to_chat(file_info)
        
        # Компактное содержимое
        content_items = [
            ft.Text(original_name[:35] + "..." if len(original_name) > 35 else original_name, 
                   size=11, weight=ft.FontWeight.BOLD),
            rename_field,
        ]
        
        # Добавляем чекбокс одноразового просмотра только для медиа
        if is_media:
            content_items.append(one_time_checkbox)
        
        rename_dialog = ft.AlertDialog(
            title=ft.Text("Отправка файла", size=15),
            content=ft.Container(
                content=ft.Column(content_items, tight=True, spacing=10),
                width=280,
            ),
            actions=[
                ft.TextButton("Отмена", on_click=lambda e: page.close(rename_dialog)),
                ft.TextButton("Отправить", on_click=confirm_rename),
            ],
        )
        page.open(rename_dialog)

            # FilePicker для выбора файлов - ВЫНЕСЕН НАВЕРХ!
    def on_file_picked(e: ft.FilePickerResultEvent):
            if e.files:
                for file in e.files:
                    file_info = {
                        'path': file.path,
                        'name': file.name,
                        'display_name': file.name
                    }
                    # Показываем диалог переименования
                    show_rename_dialog(file_info)
        
    file_picker = ft.FilePicker(on_result=on_file_picked)
    page.overlay.append(file_picker)
    
    def add_file_to_chat(file_info):
        file_path = file_info['path']
        display_name = file_info['display_name']
        one_time_view = file_info.get('one_time_view', False)
        file_ext = os.path.splitext(display_name)[1].lower()
        
        # Автосохранение файла
        saved_path = auto_save_file(file_path, display_name)
        
        # Определяем тип файла
        file_type = "document"
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            file_type = "image"
        elif file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            file_type = "video"
        elif file_ext in ['.mp3', '.wav', '.ogg', '.m4a']:
            file_type = "audio"
        
        # Отправляем файл через WebSocket
        send_file_via_websocket(saved_path, display_name, file_type, one_time_view)
        
        # Создаем сообщение в чате (как и раньше)
        msg = None
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            msg = create_image_message(saved_path, display_name, is_user=True, one_time_view=one_time_view)
        elif file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            msg = create_video_message(saved_path, display_name, is_user=True)
        elif file_ext in ['.mp3', '.wav', '.ogg', '.m4a']:
            msg = create_audio_message(saved_path, display_name, is_user=True, one_time_view=one_time_view)
        else:
            msg = create_document_message(saved_path, f"📎 {display_name}", "Файл", is_user=True)
        
        if msg:
            messages_column.controls.append(msg)
            all_messages.append(msg)
            sent_media_files.append({
                'name': display_name,
                'type': file_ext,
                'path': saved_path
            })
        
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
    
    def on_input_change(e):
        # Переключаем видимость кнопок в зависимости от содержимого поля
        if message_input.value.strip():
            mic_button.visible = False
            attach_button.visible = False
            send_button.visible = True
        else:
            mic_button.visible = True
            attach_button.visible = True
            send_button.visible = False
        mic_button.update()
        attach_button.update()
        send_button.update()
    
    # Функция удаления сообщения
    def delete_message(message_widget):
        try:
            if message_widget in messages_column.controls:
                messages_column.controls.remove(message_widget)
                if message_widget in all_messages:
                    all_messages.remove(message_widget)
                messages_column.update()
                page.open(
                    ft.SnackBar(content=ft.Text("✅ Сообщение удалено"), duration=2000)
                )
                page.update()
        except Exception as e:
            print(f"Ошибка удаления: {e}")
    
    # Функция показа меню сообщения
    def show_message_menu(e, message_widget, message_text, is_user):
        def close_menu(e):
            page.close(menu_dialog)
        
        def delete_action(e):
            delete_message(message_widget)
            page.close(menu_dialog)
        
        def copy_action(e):
            page.set_clipboard(message_text)
            page.open(
                ft.SnackBar(content=ft.Text("📋 Скопировано!"), duration=2000)
            )
            page.update()
            page.close(menu_dialog)
        
        # Создаем меню
        menu_items = [
            ft.TextButton("📋 Копировать", on_click=copy_action),
        ]
        
        # Кнопка удаления только для своих сообщений
        if is_user:
            menu_items.append(
                ft.TextButton("🗑️ Удалить", on_click=delete_action)
            )
        
        menu_dialog = ft.AlertDialog(
            title=ft.Text("Действия"),
            content=ft.Column(
                menu_items,
                tight=True,
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=close_menu),
            ],
        )
        
        page.open(menu_dialog)
    
    message_input = ft.TextField(
        hint_text="Введите сообщение...",
        expand=True,
        multiline=True,
        min_lines=1,
        max_lines=3,
        on_change=on_input_change,
    )
    
    # Функция для создания обычного сообщения
    def create_chat_message(message: str, is_user: bool = True):
        # Создаем аватар с фото или текстом
        user_data = CURRENT_USER if is_user else CONTACT_USER
        avatar = create_avatar_widget(user_data)
        
        message_bubble = ft.Container(
            content=ft.Column(
                [
                    ft.Text(message, color=ft.Colors.WHITE),
                    ft.Text(
                        datetime.datetime.now().strftime("%H:%M"),
                        size=12,
                        color=ft.Colors.WHITE54,
                    ),
                ],
                tight=True,
                spacing=2,
            ),
            bgcolor=ft.Colors.BLUE if is_user else ft.Colors.GREY,
            padding=10,
            border_radius=15,
            margin=ft.margin.only(right=10) if is_user else ft.margin.only(left=10),
        )
        
        # Создаем строку сообщения
        if is_user:
            message_row = ft.Row(
                [
                    ft.Container(expand=True),
                    message_bubble,
                    avatar,
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        else:
            message_row = ft.Row(
                [
                    avatar,
                    message_bubble,
                    ft.Container(expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        
        # Делаем сообщение кликабельным для меню
        clickable_message = ft.GestureDetector(
            content=message_row,
            on_long_press_start=lambda e: show_message_menu(e, clickable_message, message, is_user),
            on_tap=lambda e: show_message_menu(e, clickable_message, message, is_user),
        )
        
        return clickable_message
    
    # Функция для создания сообщения с изображением
    def create_image_message(image_path: str, file_name: str, is_user: bool = True, one_time_view: bool = False):
        # Создаем аватар с фото или текстом
        user_data = CURRENT_USER if is_user else CONTACT_USER
        avatar = create_avatar_widget(user_data)
        
        # ID для одноразового просмотра
        message_id = f"img_{datetime.datetime.now().timestamp()}"
        is_viewed = [message_id in viewed_one_time_messages]
        
        def open_one_time_image(e):
            if one_time_view:
                if is_viewed[0]:
                    # Уже просмотрено
                    page.open(
                        ft.SnackBar(content=ft.Text("❌ Это сообщение уже было просмотрено"), duration=2000)
                    )
                    page.update()
                    return
                
                # Помечаем как просмотренное
                viewed_one_time_messages.append(message_id)
                is_viewed[0] = True
                
                # Показываем изображение
                def close_and_delete(e):
                    page.close(image_dialog)
                    # Заменяем изображение на заглушку
                    replace_with_viewed_placeholder()
                
                image_dialog = ft.AlertDialog(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Image(
                                    src=image_path,
                                    fit=ft.ImageFit.CONTAIN,
                                ),
                                ft.Text("⚠️ Одноразовый просмотр", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.RED),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        width=600,
                        height=650,
                    ),
                    actions=[
                        ft.TextButton("Закрыть", on_click=close_and_delete),
                    ],
                )
                page.open(image_dialog)
            else:
                # Обычный просмотр
                open_image_fullscreen(image_path, file_name)
        
        def replace_with_viewed_placeholder():
            # Заменяем содержимое на заглушку
            image_container.content = ft.Column(
                [
                    ft.Icon(ft.Icons.VISIBILITY_OFF, size=80, color=ft.Colors.WHITE54),
                    ft.Text(
                        "Просмотрено",
                        size=16,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        datetime.datetime.now().strftime("%H:%M"),
                        size=12,
                        color=ft.Colors.WHITE54,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
            image_container.update()
        
        # Проверяем, было ли уже просмотрено
        if one_time_view and is_viewed[0]:
            image_content = ft.Column(
                [
                    ft.Icon(ft.Icons.VISIBILITY_OFF, size=80, color=ft.Colors.WHITE54),
                    ft.Text(
                        "Просмотрено",
                        size=16,
                        color=ft.Colors.WHITE,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        datetime.datetime.now().strftime("%H:%M"),
                        size=12,
                        color=ft.Colors.WHITE54,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        else:
            image_content = ft.Column(
                [
                    ft.Stack(
                        [
                            ft.Image(
                                src=image_path,
                                width=200,
                                height=200,
                                fit=ft.ImageFit.COVER,
                                border_radius=10,
                            ),
                            # Иконка одноразового просмотра
                            ft.Container(
                                content=ft.Icon(ft.Icons.VISIBILITY, color=ft.Colors.WHITE, size=30),
                                alignment=ft.alignment.center,
                                width=200,
                                height=200,
                            ) if one_time_view else ft.Container(),
                        ],
                    ),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.TIMER_OUTLINED, color=ft.Colors.WHITE, size=16) if one_time_view else ft.Container(),
                            ft.Text(
                                file_name if not one_time_view else "Одноразовое фото",
                                size=12,
                                color=ft.Colors.WHITE,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                icon_color=ft.Colors.WHITE,
                                icon_size=16,
                                tooltip="Скачать",
                                on_click=lambda e: download_file(image_path, file_name),
                            ) if not one_time_view else ft.Container(),
                        ],
                        spacing=5,
                    ),
                    ft.Text(
                        datetime.datetime.now().strftime("%H:%M"),
                        size=12,
                        color=ft.Colors.WHITE54,
                    ),
                ],
                tight=True,
                spacing=5,
            )
        
        # Создаем кликабельное изображение
        image_container = ft.Container(
            content=image_content,
            bgcolor=ft.Colors.BLUE_700 if is_user else ft.Colors.GREY_700,
            padding=10,
            border_radius=15,
            margin=ft.margin.only(right=10) if is_user else ft.margin.only(left=10),
        )
        
        # Создаем строку сообщения
        if is_user:
            message_row = ft.Row(
                [
                    ft.Container(expand=True),
                    image_container,
                    avatar,
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        else:
            message_row = ft.Row(
                [
                    avatar,
                    image_container,
                    ft.Container(expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        
        # Делаем кликабельным для просмотра и меню
        clickable_message = ft.GestureDetector(
            content=message_row,
            on_tap=lambda e: open_one_time_image(e),
            on_long_press_start=lambda e: show_message_menu(e, clickable_message, f"📷 Фото", is_user),
        )
        
        return clickable_message
    
    # Функция для создания сообщения с видео
    def create_video_message(video_path: str, file_name: str, is_user: bool = True):
        # Создаем аватар с фото или текстом
        user_data = CURRENT_USER if is_user else CONTACT_USER
        avatar = create_avatar_widget(user_data)
        
        # Создаем превью видео с иконкой play
        video_preview = ft.Container(
            content=ft.Column(
                [
                    ft.Stack(
                        [
                            ft.Container(
                                width=200,
                                height=150,
                                bgcolor=ft.Colors.BLACK54,
                                border_radius=10,
                            ),
                            ft.Container(
                                content=ft.Icon(
                                    ft.Icons.PLAY_CIRCLE_FILLED,
                                    color=ft.Colors.WHITE,
                                    size=60,
                                ),
                                alignment=ft.alignment.center,
                                width=200,
                                height=150,
                            ),
                        ],
                    ),
                    ft.Row(
                        [
                            ft.Text(
                                f"Vidio",
                                size=12,
                                color=ft.Colors.WHITE,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                icon_color=ft.Colors.WHITE,
                                icon_size=16,
                                tooltip="Скачать",
                                on_click=lambda e: download_file(video_path, file_name),
                            ),
                        ],
                        spacing=5,
                    ),
                    ft.Text(
                        datetime.datetime.now().strftime("%H:%M"),
                        size=12,
                        color=ft.Colors.WHITE54,
                    ),
                ],
                tight=True,
                spacing=5,
            ),
            bgcolor=ft.Colors.BLUE_700 if is_user else ft.Colors.GREY_700,
            padding=10,
            border_radius=15,
            margin=ft.margin.only(right=10) if is_user else ft.margin.only(left=10),
        )
        
        # Создаем строку сообщения
        if is_user:
            message_row = ft.Row(
                [
                    ft.Container(expand=True),
                    video_preview,
                    avatar,
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        else:
            message_row = ft.Row(
                [
                    avatar,
                    video_preview,
                    ft.Container(expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        
        # Делаем кликабельным для просмотра и меню
        clickable_message = ft.GestureDetector(
            content=message_row,
            on_tap=lambda e: open_video_viewer(video_path, file_name),
            on_long_press_start=lambda e: show_message_menu(e, clickable_message, f"Видео", is_user),
        )
        
        return clickable_message
    
    # Функция для создания сообщения с аудио (с прогресс-баром)
    def create_audio_message(audio_path: str, file_name: str, is_user: bool = True, one_time_view: bool = False):
        # Создаем аватар с фото или текстом
        user_data = CURRENT_USER if is_user else CONTACT_USER
        avatar = create_avatar_widget(user_data)
        
        # Если одноразовый просмотр, добавляем иконку
        display_name = f"" if one_time_view else file_name
        
        # Создаем аудио элемент (работающий!)
        try:
            # Используем стандартный HTML audio через data URL
            import base64
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode()
            audio_src = f"data:audio/mpeg;base64,{audio_base64}"
        except:
            audio_src = audio_path
        
        # Состояние воспроизведения
        is_playing = [False]
        current_position = [0]  # В секундах
        duration = [120]  # Примерная длительность в секундах
        timer_thread = [None]
        
        # UI элементы
        play_button = [None]
        progress_slider = [None]
        time_text = [None]
        audio_element = [None]
        
        # Форматирование времени
        def format_time(seconds):
            minutes = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{minutes}:{secs:02d}"
        
        # Получаем длительность аудио (примерно)
        try:
            file_size = os.path.getsize(audio_path)
            # Примерная оценка: 1 МБ ≈ 60 секунд для MP3
            duration[0] = max(30, min(300, file_size / (1024 * 1024) * 60))
        except:
            duration[0] = 60
        
        # Обработчик изменения позиции слайдера (перемотка)
        def on_slider_change(e):
            if duration[0] > 0:
                new_position = e.control.value
                current_position[0] = new_position
                time_text[0].value = f"{format_time(current_position[0])} / {format_time(duration[0])}"
                time_text[0].update()
        
        # Обработчик когда пользователь отпускает слайдер (применяем перемотку)
        def on_slider_change_end(e):
            if duration[0] > 0 and audio_element[0]:
                new_position = e.control.value
                current_position[0] = new_position
                # Перематываем аудио
                try:
                    audio_element[0].seek(int(new_position * 1000))  # В миллисекундах
                    time_text[0].value = f"{format_time(current_position[0])} / {format_time(duration[0])}"
                    time_text[0].update()
                except Exception as ex:
                    print(f"Ошибка перемотки: {ex}")
        
        # Обновление прогресса
        def update_progress():
            import threading
            if is_playing[0] and current_position[0] < duration[0]:
                current_position[0] += 0.5
                if current_position[0] > duration[0]:
                    current_position[0] = duration[0]
                    is_playing[0] = False
                    play_button[0].icon = ft.Icons.PLAY_ARROW
                    play_button[0].update()
                
                progress_slider[0].value = current_position[0]
                time_text[0].value = f"{format_time(current_position[0])} / {format_time(duration[0])}"
                progress_slider[0].update()
                time_text[0].update()
                
                # Планируем следующее обновление
                if is_playing[0]:
                    timer_thread[0] = threading.Timer(0.5, update_progress)
                    timer_thread[0].start()
        
        # Кнопка Play/Pause с реальным audio
        def toggle_play(e):
            if is_playing[0]:
                # Пауза
                is_playing[0] = False
                play_button[0].icon = ft.Icons.PLAY_ARROW
                if timer_thread[0]:
                    timer_thread[0].cancel()
                if audio_element[0]:
                    audio_element[0].pause()
            else:
                # Воспроизведение
                is_playing[0] = True
                play_button[0].icon = ft.Icons.PAUSE
                if audio_element[0]:
                    if current_position[0] == 0:
                        audio_element[0].play()
                    else:
                        audio_element[0].resume()
                update_progress()
            play_button[0].update()
        
        # Создаем Audio элемент (скрытый)
        audio = ft.Audio(
            src=audio_path,
            autoplay=False,
            volume=1,
        )
        audio_element[0] = audio
        page.overlay.append(audio)
        
        play_btn = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW,
            icon_color=ft.Colors.WHITE,
            icon_size=30,
            on_click=toggle_play,
        )
        play_button[0] = play_btn
        
        # Прогресс-бар (слайдер)
        slider = ft.Slider(
            min=0,
            max=duration[0],
            value=0,
            active_color=ft.Colors.WHITE,
            inactive_color=ft.Colors.WHITE38,
            thumb_color=ft.Colors.WHITE,
            on_change=on_slider_change,
            on_change_end=on_slider_change_end,
        )
        progress_slider[0] = slider
        
        # Текст времени
        time_display = ft.Text(
            f"0:00 / {format_time(duration[0])}",
            color=ft.Colors.WHITE70,
            size=11,
        )
        time_text[0] = time_display
        
        # Получаем размер файла
        try:
            file_size = os.path.getsize(audio_path)
            if file_size < 1024 * 1024:
                size_text = f"{file_size / 1024:.1f} КБ"
            else:
                size_text = f"{file_size / (1024 * 1024):.1f} МБ"
        except:
            size_text = ""
        
        audio_bubble = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            play_btn,
                            ft.Column(
                                [
                                    ft.Text(
                                        display_name,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD,
                                        size=13,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(
                                        f"🎵 {size_text}",
                                        color=ft.Colors.WHITE70,
                                        size=11,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                icon_color=ft.Colors.WHITE,
                                icon_size=20,
                                tooltip="Скачать",
                                on_click=lambda e: download_file(audio_path, file_name),
                            ) if not one_time_view else ft.Container(),  # Скрываем скачивание для одноразовых
                        ],
                        spacing=5,
                    ),
                    # Прогресс-бар
                    slider,
                    # Время
                    ft.Row(
                        [
                            time_display,
                            ft.Container(expand=True),
                            ft.Text(
                                datetime.datetime.now().strftime("%H:%M"),
                                size=12,
                                color=ft.Colors.WHITE54,
                            ),
                        ],
                    ),
                ],
                tight=True,
                spacing=2,
            ),
            bgcolor=ft.Colors.BLUE_700 if is_user else ft.Colors.GREY_700,
            padding=10,
            border_radius=15,
            margin=ft.margin.only(right=10) if is_user else ft.margin.only(left=10),
            width=300,
        )
        
        # Создаем строку сообщения
        if is_user:
            message_row = ft.Row(
                [
                    ft.Container(expand=True),
                    audio_bubble,
                    avatar,
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        else:
            message_row = ft.Row(
                [
                    avatar,
                    audio_bubble,
                    ft.Container(expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        
        # Делаем кликабельным для меню
        clickable_message = ft.GestureDetector(
            content=message_row,
            on_long_press_start=lambda e: show_message_menu(e, clickable_message, f"🎵 Аудио", is_user),
        )
        
        return clickable_message
    
    # Функция для создания сообщения с документом
    def create_document_message(file_path: str, file_name: str, file_type: str, is_user: bool = True):
        # Создаем аватар с фото или текстом
        user_data = CURRENT_USER if is_user else CONTACT_USER
        avatar = create_avatar_widget(user_data)
        
        # Получаем размер файла
        try:
            file_size = os.path.getsize(file_path)
            if file_size < 1024:
                size_text = f"{file_size} Б"
            elif file_size < 1024 * 1024:
                size_text = f"{file_size / 1024:.1f} КБ"
            else:
                size_text = f"{file_size / (1024 * 1024):.1f} МБ"
        except:
            size_text = "Неизвестно"
        
        document_bubble = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.INSERT_DRIVE_FILE,
                                color=ft.Colors.WHITE,
                                size=40,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        file_name,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.BOLD,
                                        size=13,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    ft.Text(
                                        f"{file_type} • {size_text}",
                                        color=ft.Colors.WHITE70,
                                        size=11,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DOWNLOAD,
                                icon_color=ft.Colors.WHITE,
                                icon_size=20,
                                tooltip="Скачать",
                                on_click=lambda e: download_file(file_path, file_name.replace("📄 ", "").replace("📝 ", "").replace("📊 ", "").replace("📃 ", "").replace("🗜️ ", "").replace("📎 ", "")),
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Text(
                        datetime.datetime.now().strftime("%H:%M"),
                        size=12,
                        color=ft.Colors.WHITE54,
                    ),
                ],
                tight=True,
                spacing=5,
            ),
            bgcolor=ft.Colors.BLUE_700 if is_user else ft.Colors.GREY_700,
            padding=10,
            border_radius=15,
            margin=ft.margin.only(right=10) if is_user else ft.margin.only(left=10),
            width=280,
        )
        
        # Создаем строку сообщения
        if is_user:
            message_row = ft.Row(
                [
                    ft.Container(expand=True),
                    document_bubble,
                    avatar,
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        else:
            message_row = ft.Row(
                [
                    avatar,
                    document_bubble,
                    ft.Container(expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.START,
            )
        
        # Делаем кликабельным для меню
        clickable_message = ft.GestureDetector(
            content=message_row,
            on_long_press_start=lambda e: show_message_menu(e, clickable_message, file_name, is_user),
        )
        
        return clickable_message

    # Функции для работы с сообщениями
    def send_voice_message(audio_path, file_name, one_time=False):
        # Автосохранение голосового сообщения
        saved_path = auto_save_file(audio_path, file_name)
        
        # Создаем аудио сообщение БЕЗ имени файла (просто "Голосовое сообщение")
        msg = create_audio_message(saved_path, "Голосовое сообщение", is_user=True, one_time_view=one_time)
        messages_column.controls.append(msg)
        all_messages.append(msg)
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        
        # Уведомление
        if auto_download_folder and saved_path != audio_path:
            page.open(
                ft.SnackBar(
                    content=ft.Text(f"✅ Голосовое сообщение сохранено"),
                    duration=2000
                )
            )
            page.update()
    
    def toggle_voice_recorder(e):
        voice_recorder.visible = not voice_recorder.visible
        if voice_recorder.visible:
            # Начинаем запись
            start_recording()
        voice_recorder.update()
    
    # Состояние записи
    recording_start_time = [None]
    recording_timer = [None]
    
    def start_recording():
        recording_start_time[0] = time.time()
        update_recording_timer()
    
    def update_recording_timer():
        if recording_start_time[0] and voice_recorder.visible:
            elapsed = int(time.time() - recording_start_time[0])
            minutes = elapsed // 60
            seconds = elapsed % 60
            recording_time_text.value = f"Запись... {minutes}:{seconds:02d}"
            recording_time_text.update()
            # Планируем следующее обновление через 1 секунду
            import threading
            threading.Timer(1.0, update_recording_timer).start()
    
    def open_file_picker(e):
        file_picker.pick_files(
            allow_multiple=True,
            dialog_title="Выберите файлы для отправки"
        )
    
    def send_message(e):
        if message_input.value.strip():
            # Отправляем текстовое сообщение
            msg_data = {
                "type": "text",
                "message": message_input.value,
                "sender_id": CURRENT_USER["id"]
            }
            
            # Создаем и добавляем сообщение в чат
            msg = create_chat_message(message=message_input.value, is_user=True)
            messages_column.controls.append(msg)
            all_messages.append(msg)
            
            # Отправляем через WebSocket
            try:
                ws.send(json.dumps(msg_data))
            except Exception as e:
                page.open(ft.SnackBar(content=ft.Text(f"❌ Ошибка отправки: {e}"), duration=3000))
            
            # Очищаем поле ввода
            message_input.value = ""
            message_input.update()
            
            # Возвращаем кнопки
            mic_button.visible = True
            attach_button.visible = True
            send_button.visible = False
            mic_button.update()
            attach_button.update()
            send_button.update()
            
            messages_column.scroll_to(offset=-1, duration=300)
            page.update()


    def send_file_via_websocket(file_path, file_name, file_type, one_time_view=False):
        """
        Отправляет файл через WebSocket в формате, который ожидает сервер
        file_type: 'image', 'video', 'audio', 'document'
        """
        try:
            # Проверяем размер файла (лимит 50 МБ как на сервере)
            file_size = os.path.getsize(file_path)
            MAX_SIZE = 50 * 1024 * 1024  # 50 МБ
            
            if file_size > MAX_SIZE:
                print(f"❌ Файл слишком большой: {file_size / 1024 / 1024:.1f} МБ (макс. 50 МБ)")
                page.open(ft.SnackBar(
                    content=ft.Text(f"❌ Файл слишком большой! Максимум 50 МБ"),
                    duration=3000
                ))
                return False
            
            # Читаем файл
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Создаем метаданные в формате, который ожидает сервер
            metadata = {
                "file_name": file_name,
                "file_type": file_type,  # сервер ожидает mime-type
                "file_size": file_size
            }
            
            # Конвертируем метаданные в JSON и потом в байты
            metadata_bytes = json.dumps(metadata).encode('utf-8')
            
            # Разделитель (точно такой же как на сервере)
            separator = b"|||BINARY_DATA|||"
            
            # Склеиваем: метаданные + разделитель + файл
            message_bytes = metadata_bytes + separator + file_data
            
            print(f"📤 Отправка файла: {file_name} ({file_size / 1024:.1f} КБ)")
            print(f"📤 Метаданные: {metadata}")
            print(f"📤 Размер сообщения: {len(message_bytes) / 1024:.1f} КБ")
            
            # Отправляем как БИНАРНЫЕ данные (не JSON!)
            ws.send_binary(message_bytes)
            
            print(f"✅ Файл отправлен: {file_name}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки файла: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ===================================================================
    # ПУБЛИЧНЫЕ ФУНКЦИИ ДЛЯ WEBSOCKET - ДОБАВЛЕНИЕ ВХОДЯЩИХ СООБЩЕНИЙ
    # ===================================================================
    # Используй эти функции когда получаешь сообщения от собеседника!
    
    def add_incoming_text_message(text, sender_id=None):
        """
        Добавляет текстовое сообщение (определяет сторону по sender_id)
        
        Args:
            text: Текст сообщения
            sender_id: ID отправителя (1=я, 2=собеседник)
            
        Пример:
            add_incoming_text_message("Привет!", sender_id=1)  # Мое (справа)
            add_incoming_text_message("Привет!", sender_id=2)  # Чужое (слева)
        """
        # ОПРЕДЕЛЯЕМ ПО sender_id КТО ОТПРАВИЛ
        is_user = (sender_id == CURRENT_USER["id"]) if sender_id is not None else False
        
        msg = create_chat_message(message=text, is_user=is_user)
        messages_column.controls.append(msg)
        all_messages.append(msg)
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        
        side = "СПРАВА (мое)" if is_user else "СЛЕВА (чужое)"
        print(f"✅ Сообщение добавлено {side}, sender_id={sender_id}: {text}")
    
    def add_incoming_image(image_path, file_name, sender_id=None, one_time_view=False):
        """
        Добавляет фото (определяет сторону по sender_id)
        
        Args:
            image_path: Путь к изображению
            file_name: Имя файла
            sender_id: ID отправителя
            one_time_view: Одноразовый просмотр
            
        Пример:
            add_incoming_image("/path/photo.jpg", "photo.jpg", sender_id=2)  # Слева
        """
        is_user = (sender_id == CURRENT_USER["id"]) if sender_id is not None else False
        
        msg = create_image_message(image_path, file_name, is_user=is_user, one_time_view=one_time_view)
        messages_column.controls.append(msg)
        all_messages.append(msg)
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        
        side = "СПРАВА" if is_user else "СЛЕВА"
        print(f"✅ Фото добавлено {side}, sender_id={sender_id}: {file_name}")
    
    def add_incoming_video(video_path, file_name, sender_id=None):
        """
        Добавляет видео (определяет сторону по sender_id)
        
        Args:
            video_path: Путь к видео
            file_name: Имя файла
            sender_id: ID отправителя
        """
        is_user = (sender_id == CURRENT_USER["id"]) if sender_id is not None else False
        
        msg = create_video_message(video_path, file_name, is_user=is_user)
        messages_column.controls.append(msg)
        all_messages.append(msg)
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        
        side = "СПРАВА" if is_user else "СЛЕВА"
        print(f"✅ Видео добавлено {side}, sender_id={sender_id}: {file_name}")
    
    def add_incoming_audio(audio_path, file_name, sender_id=None):
        """
        Добавляет аудио (определяет сторону по sender_id)
        
        Args:
            audio_path: Путь к аудио
            file_name: Имя файла
            sender_id: ID отправителя
        """
        is_user = (sender_id == CURRENT_USER["id"]) if sender_id is not None else False
        
        msg = create_audio_message(audio_path, file_name, is_user=is_user)
        messages_column.controls.append(msg)
        all_messages.append(msg)
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        
        side = "СПРАВА" if is_user else "СЛЕВА"
        print(f"✅ Аудио добавлено {side}, sender_id={sender_id}: {file_name}")
    
    def add_incoming_document(file_path, file_name, sender_id=None, file_type="Файл"):
        """
        Добавляет документ (определяет сторону по sender_id)
        
        Args:
            file_path: Путь к файлу
            file_name: Имя файла
            sender_id: ID отправителя
            file_type: Тип файла
        """
        is_user = (sender_id == CURRENT_USER["id"]) if sender_id is not None else False
        
        msg = create_document_message(file_path, file_name, file_type, is_user=is_user)
        messages_column.controls.append(msg)
        all_messages.append(msg)
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        
        side = "СПРАВА" if is_user else "СЛЕВА"
        print(f"✅ Документ добавлен {side}, sender_id={sender_id}: {file_name}")
    
    # Сохраняем функции в page.data чтобы к ним можно было обращаться извне
    page.data = {
        "add_incoming_text": add_incoming_text_message,
        "add_incoming_image": add_incoming_image,
        "add_incoming_video": add_incoming_video,
        "add_incoming_audio": add_incoming_audio,
        "add_incoming_document": add_incoming_document,
    }
    
    print("🎯 API для входящих сообщений готов!")
    print(f"📌 Текущий пользователь: {CURRENT_USER['name']}")
    print(f"📌 Собеседник: {CONTACT_USER['name']}")
    # ===================================================================

    def go_back(e):
        print("Нажата кнопка назад")
    
    def clear_all_chat():
        """Очищает весь чат"""
        def confirm_clear(e):
            messages_column.controls.clear()
            all_messages.clear()
            messages_column.update()
            page.close(clear_dialog)
            page.open(ft.SnackBar(content=ft.Text("🗑️ Чат очищен"), duration=2000))
            page.update()
        
        def cancel_clear(e):
            page.close(clear_dialog)
        
        clear_dialog = ft.AlertDialog(
            title=ft.Text("Очистить чат?"),
            content=ft.Text("Все сообщения будут удалены"),
            actions=[
                ft.TextButton("Отмена", on_click=cancel_clear),
                ft.TextButton("Очистить", on_click=confirm_clear, style=ft.ButtonStyle(color=ft.Colors.RED)),
            ],
        )
        page.open(clear_dialog)

    def show_user_profile(e):
        """Показывает полный профиль пользователя (собеседника)"""
        
        def close_profile(e):
            page.close(profile_dialog)
        
        def call_user(e):
            page.open(
                ft.SnackBar(content=ft.Text("📞 Звонок..."), duration=2000)
            )
            page.update()
        
        def video_call_user(e):
            page.open(
                ft.SnackBar(content=ft.Text("📹 Видеозвонок..."), duration=2000)
            )
            page.update()
        
        def search_messages(e):
            page.open(
                ft.SnackBar(content=ft.Text("🔍 Поиск по сообщениям..."), duration=2000)
            )
            page.update()
        
        def mute_notifications(e):
            page.open(
                ft.SnackBar(content=ft.Text("🔕 Уведомления отключены"), duration=2000)
            )
            page.update()
        
        def block_user(e):
            page.open(
                ft.SnackBar(content=ft.Text("🚫 Пользователь заблокирован"), duration=2000)
            )
            page.update()
        
        # Создаем большой аватар для профиля
        big_avatar = create_avatar_widget(CONTACT_USER, size=160)
        
        # Создаем профиль с данными из CONTACT_USER
        profile_dialog = ft.AlertDialog(
            content=ft.Container(
                content=ft.Column(
                    [
                        # Аватар большой
                        ft.Container(
                            content=big_avatar,
                            alignment=ft.alignment.center,
                            padding=20,
                        ),
                        
                        # Имя
                        ft.Text(
                            CONTACT_USER["name"],
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        
                        # Телефон
                        ft.Text(
                            CONTACT_USER["phone"],
                            size=16,
                            color=ft.Colors.GREY,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        
                        # Статус
                        ft.Container(
                            content=ft.Text(
                                CONTACT_USER["status"],
                                size=14,
                                color=ft.Colors.GREEN,
                            ),
                            alignment=ft.alignment.center,
                            padding=10,
                        ),
                        
                        ft.Divider(),
                        
                        # Кнопки действий
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.CALL,
                                            icon_color=ft.Colors.GREEN,
                                            icon_size=30,
                                            on_click=call_user,
                                            tooltip="Позвонить",
                                        ),
                                        ft.Text("Позвонить", size=12),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=5,
                                ),
                                ft.Column(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.VIDEOCAM,
                                            icon_color=ft.Colors.BLUE,
                                            icon_size=30,
                                            on_click=video_call_user,
                                            tooltip="Видеозвонок",
                                        ),
                                        ft.Text("Видео", size=12),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=5,
                                ),
                                ft.Column(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.SEARCH,
                                            icon_color=ft.Colors.ORANGE,
                                            icon_size=30,
                                            on_click=search_messages,
                                            tooltip="Поиск",
                                        ),
                                        ft.Text("Поиск", size=12),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=5,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        ),
                        
                        ft.Divider(),
                        
                        # Информация
                        ft.Container(
                            content=ft.Column(
                                [
                                    # О себе
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.INFO_OUTLINE, size=20, color=ft.Colors.GREY),
                                            ft.Column(
                                                [
                                                    ft.Text("О себе", size=12, color=ft.Colors.GREY),
                                                    ft.Text(CONTACT_USER["about"], size=14),
                                                ],
                                                spacing=2,
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                    
                                    ft.Divider(height=20),
                                    
                                    # Медиа
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.PHOTO_LIBRARY, size=20, color=ft.Colors.GREY),
                                            ft.Column(
                                                [
                                                    ft.Text("Отправленные файлы", size=12, color=ft.Colors.GREY),
                                                    ft.Text(f"{len(sent_media_files)} файлов", size=14),
                                                ],
                                                spacing=2,
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                    
                                    ft.Divider(height=20),
                                    
                                    # Сообщения
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.CHAT_BUBBLE_OUTLINE, size=20, color=ft.Colors.GREY),
                                            ft.Column(
                                                [
                                                    ft.Text("Сообщений", size=12, color=ft.Colors.GREY),
                                                    ft.Text(f"{len(all_messages)} сообщений", size=14),
                                                ],
                                                spacing=2,
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                ],
                                spacing=10,
                            ),
                            padding=10,
                        ),
                        
                        ft.Divider(),
                        
                        # Дополнительные действия
                        ft.Column(
                            [
                                ft.TextButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.Icons.NOTIFICATIONS_OFF, color=ft.Colors.GREY),
                                            ft.Text("Отключить уведомления", size=14),
                                        ],
                                        spacing=10,
                                    ),
                                    on_click=mute_notifications,
                                ),
                                ft.TextButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(ft.Icons.BLOCK, color=ft.Colors.RED),
                                            ft.Text("Заблокировать", size=14, color=ft.Colors.RED),
                                        ],
                                        spacing=10,
                                    ),
                                    on_click=block_user,
                                ),
                            ],
                            spacing=5,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                ),
                width=400,
                height=700,
            ),
            actions=[
                ft.TextButton("Закрыть", on_click=close_profile),
            ],
        )
        
        page.open(profile_dialog)

    # Функция для создания шапки чата
    def create_chat_header():
        # Создаем аватар собеседника для шапки
        contact_avatar = create_avatar_widget(CONTACT_USER)
        
        return ft.Container(
            content=ft.Row(
                [
                    # Кнопка назад
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK,
                        on_click=go_back,
                        icon_color=ft.Colors.BLUE,
                    ),
                    # Кликабельная зона с аватаром и информацией собеседника
                    ft.GestureDetector(
                        content=ft.Row(
                            [
                                contact_avatar,
                                ft.Column(
                                    [
                                        ft.Text(CONTACT_USER["name"], weight=ft.FontWeight.BOLD, size=16),
                                        ft.Text(CONTACT_USER["last_seen"], size=12, color=ft.Colors.GREY),
                                    ],
                                    spacing=0,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        on_tap=show_user_profile,
                    ),
                    ft.Container(expand=True),
                    # Кнопка очистки чата
                    ft.IconButton(
                        icon=ft.Icons.DELETE_SWEEP,
                        icon_color=ft.Colors.RED,
                        tooltip="Очистить весь чат",
                        on_click=lambda e: clear_all_chat(),
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=15,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.only(bottom=ft.border.BorderSide(1, ft.Colors.GREY_300)),
        )

    # Создаем панель записи голоса
    recording_time_text = ft.Text("Запись... 0:00", size=14)
    
    def create_voice_recorder():
        
        # Чекбокс для одноразового просмотра
        voice_one_time_checkbox = ft.Checkbox(
            label="Одноразовый",
            value=False,
        )
        
        def cancel_recording():
            voice_container.visible = False
            recording_start_time[0] = None
            voice_one_time_checkbox.value = False  # Сбрасываем
            voice_container.update()
        
        def send_recording():
            # Создаем файл голосового сообщения
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"voice_{timestamp}.mp3"
            file_path = os.path.join(voice_recordings_folder, file_name)
            
            # Симуляция создания файла
            try:
                with open(file_path, 'w') as f:
                    f.write("")
                
                # Отправляем с учетом одноразового просмотра (но НЕ показываем имя файла)
                send_voice_message(file_path, file_name, one_time=voice_one_time_checkbox.value)
                page.open(
                    ft.SnackBar(
                        content=ft.Text("⚠️ Это демо-версия. В реальном приложении здесь будет настоящая запись."),
                        duration=3000
                    )
                )
                page.update()
            except Exception as e:
                print(f"Ошибка создания файла: {e}")
            
            voice_container.visible = False
            recording_start_time[0] = None
            voice_one_time_checkbox.value = False
            voice_container.update()
        
        voice_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Запись голосового", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.MIC, color=ft.Colors.RED, size=30),
                            recording_time_text,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    voice_one_time_checkbox,  # Чекбокс
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Отмена",
                                on_click=lambda e: cancel_recording(),
                                bgcolor=ft.Colors.GREY_300,
                            ),
                            ft.ElevatedButton(
                                "Отправить",
                                on_click=lambda e: send_recording(),
                                bgcolor=ft.Colors.BLUE,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            visible=False,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLACK54,
                offset=ft.Offset(0, 0),
            ),
        )
        
        return voice_container

    # Создаем компоненты
    voice_recorder = create_voice_recorder()
    
    # Присваиваем кнопки к глобальным переменным
    mic_button = ft.IconButton(
        icon=ft.Icons.KEYBOARD_VOICE,
        on_click=toggle_voice_recorder,
        icon_color=ft.Colors.BLUE,
        visible=True,
    )
    
    attach_button = ft.IconButton(
        icon=ft.Icons.ATTACH_FILE,
        on_click=open_file_picker,
        icon_color=ft.Colors.BLUE,
        visible=True,
        tooltip="Прикрепить файл",
    )
    
    send_button = ft.IconButton(
        icon=ft.Icons.SEND,
        on_click=send_message,
        icon_color=ft.Colors.BLUE,
        visible=False,
    )

    # Создаем шапку чата
    chat_header = create_chat_header()

    # Панель ввода сообщения
    input_row = ft.Container(
        content=ft.Row(
            [
                # Кнопка скрепки (показывается когда поле пустое)
                attach_button,
                # Поле ввода
                message_input,
                # Кнопка микрофона (показывается когда поле пустое)
                mic_button,
                # Кнопка отправки (показывается когда есть текст)
                send_button,
            ],
            vertical_alignment=ft.CrossAxisAlignment.END,
        ),
        padding=10,
        bgcolor=ft.Colors.WHITE,
    )

    # Добавляем начальные сообщения с данными пользователей
    # Добавляем начальные сообщения с данными пользователей
    initial_messages = [
        create_chat_message("Привет! Как дела?", is_user=False),
        create_chat_message("Привет! Все отлично, спасибо! А у тебя?", is_user=True),
        create_chat_message("Тоже всё хорошо! Что нового?", is_user=False),
    ]
    messages_column.controls.extend(initial_messages)
    all_messages.extend(initial_messages)

    def check_messages():
            try:
                while not message_queue.empty():
                    msg = message_queue.get_nowait()
                    
                    # Проверяем тип сообщения
                    if "type" in msg and msg["type"] == "file":
                        # Это файл!
                        handle_incoming_file(msg)
                    else:
                        # Это текстовое сообщение
                        sender_id = msg.get("sender_id")
                        text = msg.get("message")
                        
                        if text and sender_id == CONTACT_USER["id"]:
                            msg_widget = create_chat_message(text, is_user=False)
                            messages_column.controls.append(msg_widget)
                            all_messages.append(msg_widget)
                            messages_column.scroll_to(offset=-1, duration=300)
                            page.update()
                            print(f"📨 Получено сообщение от друга: {text}")
                        
            except queue.Empty:
                pass
            threading.Timer(0.5, check_messages).start()

    def handle_incoming_file(file_msg):
        """Обрабатывает входящий файл"""
        try:
            # Получаем данные файла
            file_name = file_msg.get("file_name")
            file_type = file_msg.get("file_type")
            file_data_b64 = file_msg.get("file_data")
            sender_id = file_msg.get("sender_id")
            
            print(f"📥 Обработка входящего файла: {file_name}")
            print(f"📥 Тип: {file_type}, отправитель: {sender_id}")
            
            # Декодируем из base64
            file_data = base64.b64decode(file_data_b64)
            print(f"✅ Декодировано: {len(file_data) / 1024:.1f} КБ")
            
            # Сохраняем файл
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = f"{timestamp}_{file_name}"
            file_path = os.path.join(INCOMING_FILES_FOLDER, safe_name)
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            print(f"💾 Файл сохранен: {file_path}")
            
            # Показываем в чате (только если файл от друга!)
            if sender_id == CONTACT_USER["id"]:
                if file_type == "image" or file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                    msg_widget = create_image_message(file_path, file_name, is_user=False)
                elif file_type == "video" or file_name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.webm')):
                    msg_widget = create_video_message(file_path, file_name, is_user=False)
                elif file_type == "audio" or file_name.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                    msg_widget = create_audio_message(file_path, file_name, is_user=False)
                else:
                    msg_widget = create_document_message(file_path, f"📎 {file_name}", "Файл", is_user=False)
                
                messages_column.controls.append(msg_widget)
                all_messages.append(msg_widget)
                messages_column.scroll_to(offset=-1, duration=300)
                page.update()
                
                print(f"📨 Файл от друга отображен в чате: {file_name}")
            else:
                print(f"⏭️ Файл от себя (sender_id={sender_id}), игнорируем")
            
        except Exception as e:
            print(f"❌ Ошибка при получении файла: {e}")
            import traceback
            traceback.print_exc()

    # Запускаем проверку сообщений (ТОЛЬКО ОДИН РАЗ!)
    check_messages()

    # Основной контейнер чата
    chat_container = ft.Container(
        content=ft.Column(
            [
                chat_header,
                ft.Container(
                    content=messages_column,
                    expand=True,
                    padding=10,
                    bgcolor=ft.Colors.GREY_100,
                ),
                voice_recorder,
                input_row,
            ],
            expand=True,
        ),
        expand=True,
    )

    # Добавляем чат на страницу
    page.add(chat_container)
    
    # Показываем подсказку при первом запуске
    '''if not auto_download_folder:
        page.open(
            ft.SnackBar(
                content=ft.Text("Совет: Нажмите на иконку папки 📁 вверху, чтобы выбрать папку для автосохранения файлов"),
                duration=5000
            )
        )
        page.update()'''

if __name__ == "__main__":
    ft.app(target=main)