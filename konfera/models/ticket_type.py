from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import FromToModel

STATUSES = (
    ('na', _('Not available yet')),
    ('active', _('Active')),
    ('expired', _('Expired')),
)


class TicketType(FromToModel):

    TICKET_TYPE_CHOICES = (
        ('volunteer', _('Volunteer')),
        ('press', _('Press')),
        ('student', _('Student')),
        ('attendee', _('Attendee')),
        ('supporter', _('Supporter')),
        ('speaker', _('Speaker')),
        ('sponsor', _('Sponsor')),
        ('aid', _('Aid')),
    )

    ACCESSIBILITY = (
        ('public', _('Public')),
        ('private', _('Private')),
        ('disabled', _('Disabled')),
    )

    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])
    attendee_type = models.CharField(choices=TICKET_TYPE_CHOICES, max_length=32, default='attendee')
    accessibility = models.CharField(choices=ACCESSIBILITY, max_length=32, default='private')
    usage = models.IntegerField(default=10, help_text=_('Amount of tickets that can be issued.'))
    event = models.ForeignKey('Event')

    def __str__(self):
        return self.title

    def _get_current_status(self):
        now = timezone.now()
        status = 'active'

        if not self.date_from or not self.date_to or now < self.date_from:
            status = 'na'
        elif self.date_to < now:
            status = 'expired'

        return status

    @property
    def status(self):
        return STATUSES[self._get_current_status()]

    def clean(self):
        now = timezone.now()

        if hasattr(self, 'event'):
            if (not self.date_from or not self.date_to) and now > self.event.date_to:
                raise ValidationError(_('You are creating ticket type for event that has already ended. '
                                        'Please add the dates manually.'))

            if not self.date_from:
                self.date_from = now

            if not self.date_to:
                self.date_to = self.event.date_to

            msg = _('You can\'t sell tickets after your event has ended.')
            if self.date_from > self.event.date_to:
                raise ValidationError({'date_from': msg})

            if self.date_to > self.event.date_to:
                raise ValidationError({'date_to': msg})

        super(TicketType, self).clean()
