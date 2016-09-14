from django.db import models
from konfera.models import TicketType, DiscountCodes, Order

TICKET_STATUS = (
    ('requested', 'Requested'),
    ('registered', 'Registered'),
    ('checked-in', 'Checked-in'),
    ('cancelled', 'Cancelled'),
)


class Ticket(models.Model):
    type = models.ForeignKey(TicketType, null=False)
    discount_code = models.ForeignKey(DiscountCodes, null=False)
    status = models.CharField(choices=TICKET_STATUS, max_length=32)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField()
    phone = models.CharField(max_length=64)
    description = models.TextField()
    order = models.ForeignKey(Order, null=False)

    def __str__(self):
        return "Ticket of Mr/Mrs/Ms {}".format(self.last_name)
