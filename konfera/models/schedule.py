from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Schedule(models.Model):
    start = models.DateTimeField()
    description = models.TextField(
        help_text=_('Description will be displayed, only if there is no related talk, eg. coffee break, lunch etc...'))
    talk = models.ForeignKey('Talk')
    duration = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(300),
            MinValueValidator(0)
        ],
        help_text=_('Duration in minutes.'))
    room = models.ForeignKey('Room')

    def __str__(self):
        return '%s (%s min)' % (self.start, self.duration)
