from django.db import models
from django.contrib.auth.hashers import check_password


# Create your models here.
class Models(models.Model):
    login = models.CharField(max_length=225, unique=True)
    email = models.EmailField(unique=True)
    number = models.TextField()
    status = models.TextField()
    password = models.TextField()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.login
    

# 2. ДАННЫЕ ПОЛЬЗОВАТЕЛЯ
class UserData(models.Model):
    user = models.OneToOneField(Models, on_delete=models.CASCADE)
    contacs = models.TextField()
    rooms = models.TextField()
    groups = models.TextField()


# 3. СООБЩЕНИЯ
class Message(models.Model):
    sender = models.ForeignKey(Models, on_delete=models.CASCADE, related_name='sent')
    my_message = models.TextField()
    user_message = models.TextField()
    room = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='chat/photos/%Y/%m/%d/', blank=True, null=True)
    file = models.FileField(upload_to='chat/files/%Y/%m/%d/', blank=True, null=True)
    voice_message = models.FileField(upload_to='chat/voice/%Y/%m/%d/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.sender.login}: {self.text[:30]}"

