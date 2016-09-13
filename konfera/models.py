from django.db import models


# Create your models here.
class Room(models.Model):
    title = models.CharField(max_length=128)
    
    def __str__(self):
        return self.title
