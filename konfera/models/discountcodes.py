from django.db import models
from .tickettype import TicketType


class DiscountCodes(models.Model):
    title = models.CharField(max_length=128)
    hash = models.CharField(max_length=64)
    discount = models.IntegerField(max(100), min(0))
    available_from = models.DateTimeField()
    available_to = models.DateTimeField()
    usage = models.IntegerField()
    ticket_type = models.ForeignKey(TicketType, null=False)

    def __str__(self):
        return self.title
