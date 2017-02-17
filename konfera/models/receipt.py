from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import AddressModel


class Receipt(AddressModel):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='receipt_of')
    title = models.CharField(max_length=128, verbose_name=_('Name'), blank=True)
    companyid = models.CharField(max_length=32, blank=True, verbose_name=_('Company ID'))
    taxid = models.CharField(max_length=32, blank=True, verbose_name=_('TAX ID'))
    vatid = models.CharField(max_length=32, blank=True, verbose_name=_('VAT ID'))
    amount = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])

    def __str__(self):
        return self.title
