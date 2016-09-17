from django.db import models


class Receipt(models.Model):
    title = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    street2 = models.CharField(max_length=128, blank=True, null=True)
    city = models.CharField(max_length=128)
    postcode = models.CharField(max_length=12)
    state = models.CharField(max_length=128)
    companyid = models.CharField(max_length=32, blank=True, null=True)
    taxid = models.CharField(max_length=32, blank=True, null=True)
    vatid = models.CharField(max_length=32, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12)

    def __str__(self):
        return self.title
