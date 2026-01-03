import flet as ft

def main(page: ft.Page):
    # 1. Создаем контейнер для изображения (с пустым src!)
    img = ft.Image(
        src="https://www.bleepingcomputer.com/news/security/kali-linux-20231-introduces-purple-distro-for-defensive-security/",  # Инициализируем пустой строкой
        width=300,
        height=300,
        fit=ft.ImageFit.CONTAIN
    )

    # 2. FilePicker для выбора файла
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)

    # 3. При выборе файла - грузим его в img
    def on_pick(e):
        print("Сработал on_pick!")  # Проверяем, вызывается ли функция
        if e.files:
            print("Выбран файл:", e.files[0].name)
            img.src = e.files[0].url if e.files[0].url else e.files[0].path
            img.update()
        else:
            print("Файл не выбран (e.files пуст)")
    
    # 4. Кнопка выбора
    btn = ft.ElevatedButton(
        "Выбрать фото",
        on_click=lambda _: file_picker.pick_files(
            allow_multiple=False,  # Разрешаем только один файл
            allowed_extensions=["jpg", "jpeg", "png"],
            file_type=ft.FilePickerFileType.IMAGE,
        ),
    )

    # 5. Добавляем всё на страницу
    page.add(btn, img)

    # 6. Привязываем обработчик
    file_picker.on_result = on_pick

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)