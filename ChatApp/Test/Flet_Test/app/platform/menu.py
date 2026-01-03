import flet as ft

def main_menu(page):
    page.title = 'AppChat'

    appbar = ft.AppBar(
        adaptive=True,
        leading=ft.Icon(ft.Icons.CHAT),
        leading_width=40,
        title=ft.Text("AppChat"),
        center_title=False,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions=[
            ft.PopupMenuButton(
                items=[
                ft.PopupMenuItem(
                    content=ft.Column(
                        controls=[
                            ft.CircleAvatar(
                                foreground_image_src='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.clipartmax.com%2Fpng%2Fsmall%2F321-3216004_by-default-most-linux-distributions-including-arch-arch-linux-logo-png.png&f=1&nofb=1&ipt=c7db910b5dc0d619de9abe563dcd75139aaeb4b7328d4ee1e8e890500ef8bc90',
                                radius=50,  # Увеличиваем размер аватарки
                                #on_click=open_profile_editor,
                            ),
                            ft.Text("Root", weight="bold", size=14),
                            ft.Text("#Уфайла нету цели толька путь", size=12, color="grey"),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                    ),
                    #on_click=open_profile_editor,
                    #checked=False
                ),
                ft.PopupMenuItem(),  # Разделитель (пустая строка)
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.PLUS_ONE_ROUNDED, size=20),
                            ft.Text('Новый чат'),
                        ],
                        spacing=10,
                    ),
                    #on_click=new_chat
                ),
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.DATA_SAVER_OFF, size=20),
                            ft.Text("Cтатус"),
                        ],
                        spacing=10,
                    ),
                    on_click= lambda _: page.go('/status')
                ),
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.SETTINGS_OUTLINED, size=20),
                            ft.Text("Настройки"),
                        ],
                        spacing=10,
                    ),
                    on_click= lambda _: page.go('/settings')
                ),
                ft.PopupMenuItem(),
                ft.PopupMenuItem(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LOGIN, size=20),
                            ft.Text("Выйти"),
                        ],
                        spacing=10,
                    ),
                    #on_click= lambda _: page.go('/get_out')
                ),
            ]
            ),
        ],
    )

    '''navigation_bar = ft.NavigationBar(
        adaptive=True,
        on_change=handle_nav_change,
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.CHAT, 
                selected_icon=ft.Icons.CHAT, 
                label="Чаты",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.DATA_SAVER_OFF,
                selected_icon=ft.Icons.DATA_SAVER_OFF,
                label="Статус",
            ),
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Настройки",
            ),
        ],
    )'''

    tabs = ft.Tabs(
        adaptive=True,
        selected_index=1,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Все",
                content=ft.Container(
                    content=ft.Text("Здесь пока что ничего нет!"), 
                    alignment=ft.alignment.center,
                ),
            ),
            ft.Tab(
                text='Избранное',
                content=ft.Container(
                    content=ft.Text("Здесь пока что ничего нет!"), 
                    alignment=ft.alignment.center
                ),
            ),
            ft.Tab(
                text="Группы",
                content=ft.Container(
                    content=ft.Text("Здесь пока что ничего нет!"), 
                    alignment=ft.alignment.center
                ),
            ),
        ],
        expand=1,
    )

    return ft.View(
        "/",
        [tabs],
        appbar=appbar,
        #navigation_bar=navigation_bar
    )
