from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import FromToModel


NOT_AVAILABLE = 'na'
ACTIVE = 'active'
EXPIRED = 'expired'

STATUSES = {
    NOT_AVAILABLE: _('Not available yet'),
    ACTIVE: _('Active'),
    EXPIRED: _('Expired'),
}

VOLUNTEER = 'volunteer'
PRESS = 'press'
STUDENT = 'student'
ATTENDEE = 'attendee'
SUPPORTER = 'supporter'
SPEAKER = 'speaker'
SPONSOR = 'sponsor'
AID = 'aid'

TICKET_TYPE_CHOICES = (
    (VOLUNTEER, _('Volunteer')),
    (PRESS, _('Press')),
    (STUDENT, _('Student')),
    (ATTENDEE, _('Attendee')),
    (SUPPORTER, _('Supporter')),
    (SPEAKER, _('Speaker')),
    (SPONSOR, _('Sponsor')),
    (AID, _('Aid')),
)

PUBLIC = 'public'
PRIVATE = 'private'
DISABLED = 'disabled'

ACCESSIBILITY = (
    (PUBLIC, _('Public')),
    (PRIVATE, _('Private')),
    (DISABLED, _('Disabled')),
)


class TicketType(FromToModel):
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    price = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])
    attendee_type = models.CharField(choices=TICKET_TYPE_CHOICES, max_length=32, default=ATTENDEE)
    accessibility = models.CharField(choices=ACCESSIBILITY, max_length=32, default=PRIVATE)
    usage = models.IntegerField(default=10, help_text=_('Amount of tickets that can be issued.'))
    event = models.ForeignKey('Event')

    def __str__(self):
        return self.title

    def _get_current_status(self):
        now = timezone.now()
        status = ACTIVE

        if not self.date_from or not self.date_to or now < self.date_from:
            status = NOT_AVAILABLE
        elif self.date_to < now:
            status = EXPIRED

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
