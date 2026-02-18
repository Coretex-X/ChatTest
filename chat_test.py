import flet as ft
import datetime
import os
import shutil
import json
import time
import base64

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

CURRENT_USER = {
    "id": 1,
    "name": "N",
    "avatar_text": "N",
    "avatar_color": ft.Colors.BLUE,
    "avatar_path": "/home/archlinux05/Home/b50dd6b1ebc7e97c3e5fe2d9e85f9a7a.jpg",  # ← УКАЖИ ПУТЬ К СВОЕМУ ФОТО ЗДЕСЬ! Например: "/path/to/your_photo.jpg"
    "avatar_base64": None,  # Фото в base64
    "phone": "None",
    "status": "None",
    "about": "None"
}

# Данные собеседника (с кем переписываемся)
CONTACT_USER = {
    "id": 2,
    "name": "None",
    "avatar_text": "N",
    "avatar_color": ft.Colors.GREY,
    "avatar_path": "/home/archlinux05/Home/422c80c1f7c8f7e0b5c7e2d9e85f9a7b.jpg",  # ← УКАЖИ ПУТЬ К ФОТО СОБЕСЕДНИКА ЗДЕСЬ! Например: "/path/to/friend_photo.jpg"
    "avatar_base64": None,  # Фото в base64
    "phone": "None",
    "status": "None",
    "about": "None",
    "last_seen": "None"
}

# Настройки чата
CHAT_CONFIG = {
    "room_id": "lobbi_1",
    "theme": "light",
    "notifications": True
}

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
    
    # Папка для аватарок
    avatars_folder = "avatars"
    if not os.path.exists(avatars_folder):
        os.makedirs(avatars_folder)
    
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
                    
                    # Загружаем пути к аватаркам если есть
                    if 'current_user_avatar' in settings:
                        CURRENT_USER['avatar_path'] = settings['current_user_avatar']
                    
                    if 'contact_user_avatar' in settings:
                        CONTACT_USER['avatar_path'] = settings['contact_user_avatar']
        except:
            pass
        
        # Загружаем аватарки в base64 (из кода или из настроек)
        if CURRENT_USER.get('avatar_path') and os.path.exists(CURRENT_USER['avatar_path']):
            try:
                with open(CURRENT_USER['avatar_path'], 'rb') as img_file:
                    CURRENT_USER['avatar_base64'] = base64.b64encode(img_file.read()).decode()
                print(f"✅ Загружена аватарка текущего пользователя")
            except Exception as e:
                print(f"❌ Ошибка загрузки аватарки текущего пользователя: {e}")
        
        if CONTACT_USER.get('avatar_path') and os.path.exists(CONTACT_USER['avatar_path']):
            try:
                with open(CONTACT_USER['avatar_path'], 'rb') as img_file:
                    CONTACT_USER['avatar_base64'] = base64.b64encode(img_file.read()).decode()
                print(f"✅ Загружена аватарка собеседника")
            except Exception as e:
                print(f"❌ Ошибка загрузки аватарки собеседника: {e}")
    
    # Сохранение настроек
    def save_settings():
        try:
            settings = {'auto_download_folder': auto_download_folder}
            if CURRENT_USER['avatar_path']:
                settings['current_user_avatar'] = CURRENT_USER['avatar_path']
            if CONTACT_USER['avatar_path']:
                settings['contact_user_avatar'] = CONTACT_USER['avatar_path']
            
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
        Создает виджет аватара: либо фото, либо текст
        
        Args:
            user_data: словарь с данными пользователя (CURRENT_USER или CONTACT_USER)
            size: размер аватара
            is_circle: круглая аватарка или квадратная
        """
        # Если есть фото в base64, показываем его
        if user_data.get('avatar_base64'):
            avatar = ft.Container(
                content=ft.Image(
                    src_base64=user_data['avatar_base64'],
                    fit=ft.ImageFit.COVER,
                ),
                width=size,
                height=size,
                border_radius=size//2 if is_circle else 10,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )
        # Если есть путь к фото, но нет base64 (загружаем)
        elif user_data.get('avatar_path') and os.path.exists(user_data['avatar_path']):
            try:
                with open(user_data['avatar_path'], 'rb') as img_file:
                    user_data['avatar_base64'] = base64.b64encode(img_file.read()).decode()
                
                avatar = ft.Container(
                    content=ft.Image(
                        src_base64=user_data['avatar_base64'],
                        fit=ft.ImageFit.COVER,
                    ),
                    width=size,
                    height=size,
                    border_radius=size//2 if is_circle else 10,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                )
            except:
                # Если не удалось загрузить фото, показываем текст
                avatar = ft.CircleAvatar(
                    content=ft.Text(user_data["avatar_text"], size=size//2),
                    bgcolor=user_data["avatar_color"],
                    radius=size//2,
                )
        else:
            # Нет фото, показываем текст
            avatar = ft.CircleAvatar(
                content=ft.Text(user_data["avatar_text"], size=size//2),
                bgcolor=user_data["avatar_color"],
                radius=size//2,
            )
        
        return avatar
    
    def change_avatar(user_type):
        """
        Изменение аватарки пользователя
        
        Args:
            user_type: "current" или "contact"
        """
        def on_avatar_picked(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                file_path = e.files[0].path
                file_name = e.files[0].name
                
                # Копируем файл в папку с аватарками
                dest_path = os.path.join(avatars_folder, f"{user_type}_{file_name}")
                shutil.copy2(file_path, dest_path)
                
                # Обновляем данные пользователя
                if user_type == "current":
                    CURRENT_USER['avatar_path'] = dest_path
                    with open(dest_path, 'rb') as img_file:
                        CURRENT_USER['avatar_base64'] = base64.b64encode(img_file.read()).decode()
                else:
                    CONTACT_USER['avatar_path'] = dest_path
                    with open(dest_path, 'rb') as img_file:
                        CONTACT_USER['avatar_base64'] = base64.b64encode(img_file.read()).decode()
                
                # Сохраняем настройки
                save_settings()
                
                # Обновляем интерфейс
                page.open(
                    ft.SnackBar(content=ft.Text(f"✅ Аватарка обновлена!"), duration=2000)
                )
                
                # Обновляем все аватарки в интерфейсе
                update_all_avatars()
        
        avatar_picker = ft.FilePicker(on_result=on_avatar_picked)
        page.overlay.append(avatar_picker)
        page.update()
        
        avatar_picker.pick_files(
            allow_multiple=False,
            dialog_title="Выберите фото для аватарки",
            allowed_extensions=["jpg", "jpeg", "png", "gif", "webp"]
        )
    
    def update_all_avatars():
        """Обновляет все аватарки в интерфейсе"""
        # Пересоздаем шапку чата
        nonlocal chat_header
        chat_header = create_chat_header()
        
        # Обновляем все сообщения (пересоздаем аватарки)
        for i, msg in enumerate(messages_column.controls[:]):
            if hasattr(msg, 'content') and isinstance(msg.content, ft.Row):
                # Находим аватар в сообщении и обновляем его
                for control in msg.content.controls:
                    if isinstance(control, ft.CircleAvatar) or (isinstance(control, ft.Container) and hasattr(control, 'content') and isinstance(control.content, ft.Image)):
                        # Заменяем на новый аватар
                        is_user = control in msg.content.controls[-1:] if len(msg.content.controls) > 2 else False
                        new_avatar = create_avatar_widget(CURRENT_USER if is_user else CONTACT_USER)
                        # TODO: сложная логика замены, для простоты пересоздадим сообщение
                        pass
        
        page.update()
    
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
    
    # Добавление файла в чат
    def add_file_to_chat(file_info):
        file_path = file_info['path']
        display_name = file_info['display_name']
        one_time_view = file_info.get('one_time_view', False)
        file_ext = os.path.splitext(display_name)[1].lower()
        
        # Автосохранение файла
        saved_path = auto_save_file(file_path, display_name)
        
        msg = None
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            msg = create_image_message(saved_path, display_name, is_user=True, one_time_view=one_time_view)
        elif file_ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
            msg = create_video_message(saved_path, display_name, is_user=True)
        elif file_ext in ['.mp3', '.wav', '.ogg', '.m4a']:
            msg = create_audio_message(saved_path, display_name, is_user=True)
        elif file_ext in ['.pdf']:
            msg = create_document_message(saved_path, f"📄 {display_name}", "PDF документ", is_user=True)
        elif file_ext in ['.doc', '.docx']:
            msg = create_document_message(saved_path, f"📝 {display_name}", "Word документ", is_user=True)
        elif file_ext in ['.xls', '.xlsx']:
            msg = create_document_message(saved_path, f"📊 {display_name}", "Excel таблица", is_user=True)
        elif file_ext in ['.txt']:
            msg = create_document_message(saved_path, f"📃 {display_name}", "Текстовый файл", is_user=True)
        elif file_ext in ['.zip', '.rar', '.7z']:
            msg = create_document_message(saved_path, f"🗜️ {display_name}", "Архив", is_user=True)
        else:
            msg = create_document_message(saved_path, f"📎 {display_name}", "Файл", is_user=True)
        
        if msg:
            messages_column.controls.append(msg)
            all_messages.append(msg)
            # Добавляем в список отправленных медиа файлов
            sent_media_files.append({
                'name': display_name,
                'type': file_ext,
                'path': saved_path
            })
            print(f"📎 Добавлен файл в медиа: {display_name} (всего: {len(sent_media_files)})")
        
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        
        # Уведомление об автосохранении
        if auto_download_folder and saved_path != file_path:
            page.open(
                ft.SnackBar(
                    content=ft.Text(f"✅ Файл сохранен в: {auto_download_folder}"),
                    duration=3000
                )
            )
            page.update()
    
    # FilePicker для выбора файлов
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
        """Отправка текстового сообщения"""
        if message_input.value.strip():
            # Создаем и добавляем сообщение
            msg = create_chat_message(message=message_input.value, is_user=True)
            messages_column.controls.append(msg)
            all_messages.append(msg)
            
            # Очищаем поле ввода
            message_input.value = ""
            message_input.update()
            
            # Возвращаем кнопки микрофона и скрепки после отправки
            mic_button.visible = True
            attach_button.visible = True
            send_button.visible = False
            mic_button.update()
            attach_button.update()
            send_button.update()
            
            messages_column.scroll_to(offset=-1, duration=300)
            page.update()
    
    # ===================================================================
    # ПУБЛИЧНЫЕ ФУНКЦИИ ДЛЯ WEBSOCKET - ДОБАВЛЕНИЕ ВХОДЯЩИХ СООБЩЕНИЙ
    # ===================================================================
    # Используй эти функции когда получаешь сообщения от собеседника!
    
    def add_incoming_text_message(text):
        """
        Добавляет входящее текстовое сообщение (от собеседника)
        
        Args:
            text: Текст сообщения
            
        Пример:
            add_incoming_text_message("Привет! Как дела?")
        """
        msg = create_chat_message(message=text, is_user=False)
        messages_column.controls.append(msg)
        all_messages.append(msg)
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        print(f"✅ Добавлено входящее текстовое сообщение от {CONTACT_USER['name']}: {text}")
    
    def add_incoming_image(image_path, file_name, one_time_view=False):
        """
        Добавляет входящее фото (от собеседника)
        
        Args:
            image_path: Путь к изображению
            file_name: Имя файла
            one_time_view: Одноразовый просмотр (True/False)
            
        Пример:
            add_incoming_image("/path/to/photo.jpg", "photo.jpg")
        """
        msg = create_image_message(image_path, file_name, is_user=False, one_time_view=one_time_view)
        messages_column.controls.append(msg)
        all_messages.append(msg)
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        print(f"✅ Добавлено входящее фото от {CONTACT_USER['name']}: {file_name}")
    
    def add_incoming_video(video_path, file_name):
        """
        Добавляет входящее видео (от собеседника)
        
        Args:
            video_path: Путь к видео
            file_name: Имя файла
            
        Пример:
            add_incoming_video("/path/to/video.mp4", "video.mp4")
        """
        msg = create_video_message(video_path, file_name, is_user=False)
        messages_column.controls.append(msg)
        all_messages.append(msg)
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        print(f"✅ Добавлено входящее видео от {CONTACT_USER['name']}: {file_name}")
    
    def add_incoming_audio(audio_path, file_name):
        """
        Добавляет входящее аудио (от собеседника)
        
        Args:
            audio_path: Путь к аудио
            file_name: Имя файла
            
        Пример:
            add_incoming_audio("/path/to/audio.mp3", "audio.mp3")
        """
        msg = create_audio_message(audio_path, file_name, is_user=False)
        messages_column.controls.append(msg)
        all_messages.append(msg)
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        print(f"✅ Добавлено входящее аудио от {CONTACT_USER['name']}: {file_name}")
    
    def add_incoming_document(file_path, file_name, file_type="Файл"):
        """
        Добавляет входящий документ (от собеседника)
        
        Args:
            file_path: Путь к файлу
            file_name: Имя файла
            file_type: Тип файла (например, "PDF документ")
            
        Пример:
            add_incoming_document("/path/to/doc.pdf", "📄 document.pdf", "PDF документ")
        """
        msg = create_document_message(file_path, file_name, file_type, is_user=False)
        messages_column.controls.append(msg)
        all_messages.append(msg)
        messages_column.scroll_to(offset=-1, duration=300)
        page.update()
        print(f"✅ Добавлен входящий документ от {CONTACT_USER['name']}: {file_name}")
    
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
        
        def change_avatar_action(e):
            page.close(profile_dialog)
            change_avatar("contact")
        
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
                        
                        # Кнопка изменения аватарки (маленькая иконка)
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_size=20,
                            on_click=change_avatar_action,
                            tooltip="Изменить аватарку",
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
                        on_long_press_start=lambda e: change_avatar("contact"),  # Долгое нажатие для смены аватарки
                    ),
                    ft.Container(expand=True),
                    # Кнопка очистки чата
                    ft.IconButton(
                        icon=ft.Icons.DELETE_SWEEP,
                        icon_color=ft.Colors.RED,
                        tooltip="Очистить весь чат",
                        on_click=lambda e: clear_all_chat(),
                    ),
                    # Кнопка для смены своей аватарки
                    ft.IconButton(
                        icon=ft.Icons.ACCOUNT_CIRCLE,
                        icon_color=ft.Colors.BLUE,
                        tooltip="Изменить свою аватарку",
                        on_click=lambda e: change_avatar("current"),
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
    initial_messages = [
        create_chat_message("Привет! Как дела?", is_user=False),
        create_chat_message("Привет! Все отлично, спасибо! А у тебя?", is_user=True),
        create_chat_message("Тоже всё хорошо! Что нового?", is_user=False),
    ]
    messages_column.controls.extend(initial_messages)
    all_messages.extend(initial_messages)

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