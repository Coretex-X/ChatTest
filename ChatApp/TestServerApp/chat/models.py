from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
# 2. ДАННЫЕ ПОЛЬЗОВАТЕЛЯ
class UserData(models.Model):
    user_id = models.TextField()
    guest_id = models.TextField()
    room = models.TextField()
    count = models.TextField()
    groups = models.TextField()

    def clean(self):
        # Проверяем, если запись новая, не должно быть > 1, 
        # если обновляется - не должно быть > 2 (с учетом самой себя)
        existing_count = UserData.objects.filter(room=self.room).count()
        if self.pk is None and existing_count >= 2:
            raise ValidationError('Error 404')
        elif self.pk is not None and existing_count > 2:
             raise ValidationError('Error 404')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


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
