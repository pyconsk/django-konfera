from django.db import models
from django.core.validators import MinValueValidator

from konfera.models.abstract import KonferaModel
from konfera.models.countries import COUNTRIES

COUNTRY_DEFAULT = 'SK'


class Receipt(KonferaModel):
    order = models.OneToOneField('Order', on_delete=models.DO_NOTHING, related_name='receipt_of')
    title = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    street2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128)
    postcode = models.CharField(max_length=12)
    state = models.CharField(
        choices=COUNTRIES,
        max_length=2,
        default=COUNTRY_DEFAULT)
    companyid = models.CharField(max_length=32, blank=True)
    taxid = models.CharField(max_length=32, blank=True)
    vatid = models.CharField(max_length=32, blank=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.title
