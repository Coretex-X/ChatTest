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
class DataMessage(models.Model):
    user_id = models.TextField()
    guest_id = models.TextField()
    room = models.TextField()

    my_message = models.TextField()
    my_photo = models.ImageField(upload_to='chat/photos/%Y/%m/%d/', blank=True, null=True)
    my_file = models.FileField(upload_to='chat/files/%Y/%m/%d/', blank=True, null=True)
    my_voice_message = models.FileField(upload_to='chat/voice/%Y/%m/%d/', blank=True, null=True)
    my_timestamp = models.DateTimeField(auto_now_add=True)

    guest_message = models.TextField()
    guest_photo = models.ImageField(upload_to='chat/photos/%Y/%m/%d/', blank=True, null=True)
    guest_file = models.FileField(upload_to='chat/files/%Y/%m/%d/', blank=True, null=True)
    guest_voice_message = models.FileField(upload_to='chat/voice/%Y/%m/%d/', blank=True, null=True)
    guest_timestamp = models.DateTimeField(auto_now_add=True)

