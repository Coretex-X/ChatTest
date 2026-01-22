from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path("ws/my_chat/", consumers.YourConsumer.as_asgi()),
    re_path("ws/chat_user/", consumers.PrivateChatConsumer.as_asgi()),
    re_path("ws/groop_user/", consumers.GroupChatConsumer.as_asgi()),
    re_path("ws/notifications/", consumers.NotificationConsumer.as_asgi()),

]