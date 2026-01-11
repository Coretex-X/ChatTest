from django.urls import path, include
from rest_framework import routers
from .views import *

urlpatterns = [
    #метод as_view используется для привязки класса к маршру URL-адреса 
    path('chat/', index),
]
