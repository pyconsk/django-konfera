from django.db import models
from django.core.validators import MinValueValidator

from konfera.models.abstract import AddressModel


class Receipt(AddressModel):
    order = models.OneToOneField('Order', on_delete=models.DO_NOTHING, related_name='receipt_of')
    title = models.CharField(max_length=128)
    companyid = models.CharField(max_length=32, blank=True)
    taxid = models.CharField(max_length=32, blank=True)
    vatid = models.CharField(max_length=32, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.title
