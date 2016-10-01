from django.db import models


class Room(models.Model):
    title = models.CharField(max_length=128)
    location = models.ForeignKey('Location', related_name='rooms')
    capacity = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title
