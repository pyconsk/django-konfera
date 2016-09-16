from django.db import models

from konfera.models.speaker import TITLE_UNSET, TITLE_CHOICES


TICKET_STATUS = (
    ('requested', 'Requested'),
    ('registered', 'Registered'),
    ('checked-in', 'Checked-in'),
    ('cancelled', 'Cancelled'),
)


class Ticket(models.Model):
    type = models.ForeignKey('TicketType')
    discount_code = models.ForeignKey('DiscountCodes')
    status = models.CharField(choices=TICKET_STATUS, max_length=32)
    title = models.CharField(choices=TITLE_CHOICES, max_length=4, default=TITLE_UNSET)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField()
    phone = models.CharField(max_length=64)
    description = models.TextField()
    order = models.ForeignKey('Order')

    def __str__(self):
        return '{title} {first_name} {last_name}'.format(
            title=dict(TITLE_CHOICES)[self.title],
            first_name=self.first_name,
            last_name=self.last_name
        ).strip()
