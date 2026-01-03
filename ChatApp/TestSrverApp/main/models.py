from django.db import models

# Create your models here.
class ModelsMain(models.Model):
    logo_image = models.ImageField(upload_to='images/',)