from django.db import models


class Schedule(models.Model):
    start = models.DateTimeField()
    description = models.CharField(max_length=128)
    talk = models.ForeignKey('Talk')
    duration = models.IntegerField()
    room = models.ForeignKey('Room')

    def __str__(self):
        return '%s (%s min)' % (self.start, self.duration)
