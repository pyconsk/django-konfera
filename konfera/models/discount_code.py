from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import FromToModel
from konfera.models.ticket import Ticket


class DiscountCode(FromToModel):
    title = models.CharField(max_length=128, unique=True)
    hash = models.CharField(max_length=64)
    discount = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ],
        help_text=_('Value is percentage discount from ticket type price.'),
    )
    usage = models.IntegerField(default=1, help_text=_('Amount of tickets that can be issued.'))
    ticket_type = models.ForeignKey('TicketType')

    def __str__(self):
        return self.title

    def get_usage(self):
        return len(Ticket.objects.get(discount_code=self.title))

    @property
    def is_available(self):
        return (self.usage - self.get_usage()) >= 0

    def clean(self):
        if hasattr(self, 'ticket_type'):
            if not self.date_from:
                self.date_from = self.ticket_type.date_from
            elif self.date_from < self.ticket_type.date_from:
                raise ValidationError(
                    {'date_from': _('Discount code can not be available before ticket type is available for sale.')})

            if not self.date_to:
                self.date_to = self.ticket_type.date_to
            elif self.date_to > self.ticket_type.date_to:
                raise ValidationError(
                    {'date_to': _('Discount code can not be available after ticket type is available for sale.')})

        super(DiscountCode, self).clean()
