from django.db import models


class ProcessedTransation(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=20, unique=True)
