from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class DiscountCodes(models.Model):
    title = models.CharField(max_length=128)
    hash = models.CharField(max_length=64)
    discount = models.IntegerField(default=0, validators=[
                                                    MaxValueValidator(100),
                                                    MinValueValidator(0)]
                                   )
    available_from = models.DateTimeField()
    available_to = models.DateTimeField()
    usage = models.IntegerField()
    ticket_type = models.ForeignKey('TicketType', null=False)

    def __str__(self):
        return self.title
