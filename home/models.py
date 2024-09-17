from django.db import models

# Create your models here.
class Submit(models.Model):
    email=models.CharField(max_length=124)
    password=models.CharField(max_length=124)

    def __str__(self):
        return self.email
