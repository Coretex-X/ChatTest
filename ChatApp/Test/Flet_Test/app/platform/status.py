import flet as ft

def main_status(page):
    def check_item_clicked(e):
        e.control.checked = not e.control.checked
        page.update()
    appbar = ft.AppBar(
        leading=ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=lambda _: page.go("/")),
        leading_width=40,
        title=ft.Text("Статус"),
        center_title=False,
        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        actions=[
            ft.PopupMenuButton(
                items=[
                    ft.PopupMenuItem(
                        text="Удалить статус", checked=False
                    ),
                    ft.PopupMenuItem(
                        text="Добавить статус", checked=False
                    ),
                    ft.PopupMenuItem(
                        text="Конфедициальность статуса", checked=False
                    ),
                ]
            ),
        ],
    )
    return ft.View(
        "/status",
        appbar=appbar,
    )