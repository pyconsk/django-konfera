from django.core.exceptions import ValidationError
from django.db import models
from konfera.models import TicketType


def validate_min_max(value):
    if value < 0 or value > 100:
        raise ValidationError('{} not valid Discount value'.format(value),
                              params={'value': value},
                              )


class DiscountCodes(models.Model):
    title = models.CharField(max_length=128)
    hash = models.CharField(max_length=64)
    discount = models.IntegerField(validators=[validate_min_max])   # TODO validation test needed
    available_from = models.DateTimeField()
    available_to = models.DateTimeField()
    usage = models.IntegerField()
    ticket_type = models.ForeignKey(TicketType, null=False)

    def __str__(self):
        return self.title
