from django.db import models

# Create your models here.
# 2. ДАННЫЕ ПОЛЬЗОВАТЕЛЯ
class UserData(models.Model):
    user_id = models.TextField()
    guest_id = models.TextField()
    room = models.TextField()
    count = models.TextField()
    groups = models.TextField()


# 3. СООБЩЕНИЯ
class Message(models.Model):
    my_message = models.TextField()
    user_message = models.TextField()
    room = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='chat/photos/%Y/%m/%d/', blank=True, null=True)
    file = models.FileField(upload_to='chat/files/%Y/%m/%d/', blank=True, null=True)
    voice_message = models.FileField(upload_to='chat/voice/%Y/%m/%d/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender.login}: {self.text[:30]}"

