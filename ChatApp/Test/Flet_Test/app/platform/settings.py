import flet as ft

def settings_view(page):
    user_name = "USER_NAMR"
    profile = "Привет! Я пользуюсь ChatAPP!"

    def edit_profile(e):
       pass

    # Заголовок с аватаркой и именем
    profile_header = ft.ListTile(
        leading=ft.CircleAvatar(
            content=ft.Icon(ft.Icons.SUPERVISED_USER_CIRCLE),  # Или ft.Image если есть фото
            radius=30,
        ),
        title=ft.Text(f"{user_name}", weight=ft.FontWeight.BOLD),
        subtitle=ft.Text(f"{profile}"),
        on_click=lambda e: edit_profile(page),
    )
    
    # Разделы настроек
    settings_options = [
        {"icon": ft.Icons.ACCOUNT_CIRCLE, "title": "Аккаунт",},
        {"icon": ft.Icons.CHAT, "title": "Чаты", },
        {"icon": ft.Icons.NOTIFICATIONS, "title": "Уведомления", },
        {"icon": ft.Icons.STORAGE, "title": "Хранилище и данные", },
        {"icon": ft.Icons.HELP, "title": "Помощь",},
        {"icon": ft.Icons.PEOPLE, "title": "Пригласить друзей",},
    ]
    
    # Создаем ListView с настройками
    settings_list = ft.ListView(expand=1, spacing=10)
    for option in settings_options:
        settings_list.controls.append(
            ft.ListTile(
                leading=ft.Icon(option["icon"]),
                title=ft.Text(option["title"]),
                #on_click=lambda e, action=option["action"]: action(page),
            )
        )
    
    # Собираем все вместе
    content = ft.Column(
        controls=[
            profile_header,
            ft.Divider(height=1),
            settings_list,
        ],
        expand=True,
    )

    appbar = ft.AppBar(
        leading=ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=lambda _: page.go("/")),
        leading_width=40,
        title=ft.Text("Настройки"),
        center_title=False,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
    )
    
    return ft.View(
        "/settings",
        appbar=appbar,
        controls=[content],
    )
