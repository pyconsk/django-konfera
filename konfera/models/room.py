from django.db import models


class Room(models.Model):
    title = models.CharField(max_length=128)
    room = models.ForeignKey('Location', related_name='room_locations')
    capacity = models.IntegerField(blank=True)

    def __str__(self):
        return self.title
