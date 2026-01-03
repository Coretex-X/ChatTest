import flet as ft
from menu import main_menu
from status import main_status
from settings import settings_view

def main(page: ft.Page):
    def route_change(route):
        page.views.clear()
        page.views.append(
            main_menu(page)
        )

        if page.route == "/status":
            page.views.append(
             main_status(page)
            )

        elif page.route == "/settings":
            page.views.append(
                settings_view(page)
            )

        page.update()

        

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    #page.on_view_pop = view_pop
    page.go(page.route)

ft.app(main, view=ft.AppView.WEB_BROWSER, port=8000)