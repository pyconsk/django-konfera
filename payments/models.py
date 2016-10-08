from django.db import models


class ProcessedTransation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=20, unique=True)
