import flet as ft
import httpx as hx

def main(page: ft.Page):
    page.title = "Авторизацыя"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Переменные для валидации
    required_fields = []
    error_text = ft.Text(color="red", visible=False)

    def validate_fields():
        # Проверяем все обязательные поля
        for field in required_fields:
            if not field.value:
                field.error_text = "Это поле обязательно для заполнения"
                field.update()
                return False
        return True

    async def rest_api(e):
        # Сбрасываем ошибки
        error_text.visible = False
        error_text.update()
        
        for field in required_fields:
            field.error_text = None
            field.update()

        # Валидация
        if not validate_fields():
            return
            
        # Подготовка данных
        data = {
            'login': text_input_login.value,
            'password': text_input_password.value
        }

        try:
            # Отправка на сервер
            async with hx.AsyncClient() as client:
                response = await client.post(
                    'http://127.0.0.1:7000/api/v1/user/login/',
                    json=data
                )
                
                if response.status_code == 200:
                    # Очистка полей после успешной отправки
                    text_input_login.value = ""
                    text_input_password.value = ""
                    page.update()
                else:
                    error_text.value = f"Error:{response}"
                    error_text.visible = True
                    error_text.update()
                    
        except Exception as ex:
            error_text.value = f"Ошибка соединения: {str(ex)}"
            error_text.visible = True
            error_text.update()

    # Элементы интерфейса
    label = ft.Text('Авторизация:', size=30)
    
    text_input_login = ft.TextField(
        label='Имя пользователя или E-Mail',
        autofocus=True
    )
    
    text_input_password = ft.TextField(
        label='Пароль',
        password=True,
        can_reveal_password=True
    )
      
    button = ft.ElevatedButton(
        'Войти',
        on_click=rest_api
    )
    
    or_redistration = ft.Text('Нет аккаунта?')

    button_registration = ft.ElevatedButton(
        'Зарегистрироватся',
    )

    # Добавляем поля в список обязательных
    required_fields = [
        text_input_login,
        text_input_password
    ]

    # Собираем интерфейс
    page.add(
        ft.Column([
            ft.Container(label, margin=5),
            ft.Container(text_input_login, margin=5),
            ft.Container(text_input_password, margin=5),
            ft.Container(error_text, margin=5),
            ft.Container(button, margin=5, alignment=ft.alignment.center),
            ft.Container(or_redistration, margin=5, alignment=ft.alignment.center),
            ft.Container(button_registration, margin=5, alignment=ft.alignment.center)
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        width=400
        )
    )

ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=8000)
