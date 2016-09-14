from django.db import models
from .event import Event


class TicketType(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField()
    price = models.DecimalField()
    available_from = models.DateTimeField()
    available_to = models.DateTimeField()
    event = models.ForeignKey(Event, null=False)

    def __str__(self):
        return self.title
