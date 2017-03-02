from django.db import models

from konfera.models.abstract import KonferaModel


class Room(KonferaModel):
    title = models.CharField(max_length=128)
    location = models.ForeignKey('Location', related_name='rooms')
    capacity = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

    def slugify(self):
        return self.title.strip().replace(' ', '-').lower()