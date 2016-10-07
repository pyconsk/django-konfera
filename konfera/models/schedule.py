from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import KonferaModel


class Schedule(KonferaModel):
    start = models.DateTimeField()
    event = models.ForeignKey('Event', related_name='schedules')
    description = models.TextField(
        blank=True,
        help_text=_('Description will be displayed, only if there is no related talk, eg. coffee break, lunch etc...'))
    talk = models.ForeignKey('Talk', blank=True, null=True, related_name='scheduled_talks')
    duration = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(300),
            MinValueValidator(0)
        ],
        help_text=_('Duration in minutes.'))
    room = models.ForeignKey('Room', blank=True, null=True, related_name='scheduled_rooms')

    def __str__(self):
        return _('%s (%s min)') % (self.start, self.duration)
