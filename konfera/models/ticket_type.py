from django.db import models
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import FromToModel


TICKET_TYPE_CHOICES = (
    ('volunteer', _('Volunteer')),
    ('press', _('Press')),
    ('attendee', _('Attendee')),
    ('supporter', _('Supporter')),
    ('sponsor', _('Sponsor')),
    ('aid', _('Aid')),
)


class TicketType(FromToModel):
    title = models.CharField(max_length=128)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=12)
    attendee_type = models.CharField(choices=TICKET_TYPE_CHOICES, max_length=255, default='attendee')
    event = models.ForeignKey('Event')

    def __str__(self):
        return self.title


TicketType._meta.get_field('date_from').verbose_name = _('Available from')
TicketType._meta.get_field('date_to').verbose_name = _('Available to')
