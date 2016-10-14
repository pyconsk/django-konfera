from django.db import models
from konfera.models.abstract import KonferaModel


class ProcessedTransaction(KonferaModel):
    transaction_id = models.CharField(max_length=20, unique=True)
