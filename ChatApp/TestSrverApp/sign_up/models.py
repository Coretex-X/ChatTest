from django.db import models
from django.contrib.auth.hashers import make_password, check_password

# Create your models here.
class Models(models.Model):
    login = models.CharField(max_length=225, verbose_name='Логин пользователя', unique=True)
    email = models.EmailField(verbose_name='E-Mail пользователя', unique=True)
    password = models.TextField()
    token = models.TextField()

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.login