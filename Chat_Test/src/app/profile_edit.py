import flet as ft
import json as js


def main(page: ft.Page,):
    #page.theme_mode = data["theme"]
    text_input_login = ft.TextField(
        label='Логин',
        autofocus=True
    )
    text_input = ft.TextField(
        label='Описание',
        autofocus=True
    )

    user_login = text_input_login
    profil = text_input

    bunnon = ft.ElevatedButton(
        'Сохранить',
        on_click=lambda _: page.go("/settings")
    )

    page.add(
        text_input_login,
        text_input, 
        bunnon
    )

    #return (user_login, profil)
ft.app(main, view=ft.AppView.WEB_BROWSER, port=8000)

