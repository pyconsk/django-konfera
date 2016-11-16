from django.db import models
from konfera.models.abstract import KonferaModel


class ProcessedTransaction(KonferaModel):
    transaction_id = models.CharField(max_length=20, unique=True)
    variable_symbol = models.CharField(max_length=10)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    date = models.DateField(blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True)
    executor = models.CharField(max_length=100, blank=True)
    comment = models.TextField(blank=True)
    method = models.CharField(max_length=100, default='unknown')
