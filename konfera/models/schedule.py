from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db import models
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import KonferaModel
from konfera.models.room import Room


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
        help_text=_('Duration in minutes. If talk is selected, value will be generated.'))
    room = models.ForeignKey('Room', blank=True, null=True, related_name='scheduled_rooms')

    def __str__(self):
        return _('%(start)s (%(duration)s min)') % {'start': self.start, 'duration': self.duration}

    def clean(self, *args, **kwargs):
        # Only approved talk can be scheduled
        if self.talk.status != self.talk.APPROVED:
            raise ValidationError({'talk': _('You cannot schedule unapproved talks.')})

        # Event is related to location and location has room,
        # make sure selected room in schedule belongs to Event's location
        try:
            Room.objects.get(location=self.event.location, id=self.room.id)
        except ObjectDoesNotExist:
            raise ValidationError({'room': _('The room does not belong to event location rooms.')})

        # Make sure date and time is within the event's range

        # Make sure system does not allow store two events at the same
        # time in the same room, eg. schedule datetime + duration in room is unique.
        schedules = Schedule.objects.filter(start=self.start, duration=self.duration, room=self.room)

        if schedules.exists():
            # this means that there are events with the same schedule
            raise ValidationError(_('The events in schedule cannot overlap if they are in the same room.'))

        return super().clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.talk:
            # If talk is selected duration is copied from talk
            self.duration = self.talk.duration

        return super().save(*args, **kwargs)
