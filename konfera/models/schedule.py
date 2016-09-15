from django.db import models
from konfera.models.talk import Talk
from konfera.models.room import Room


class Schedule(models.Model):
    start = models.DateTimeField()
    description = models.CharField(max_length=128)
    talk = models.ForeignKey(Talk, null=False)
    duration = models.IntegerField()
    room = models.ForeignKey(Room, null=False)

    def __str__(self):
        return '%s (%s min)' % (self.start, self.duration)
