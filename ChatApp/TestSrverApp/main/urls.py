from django.urls import path, include
from .views import *

urlpatterns = [
    path('image-create/', POST_Creat_Images.as_view())
]