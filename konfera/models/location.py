from django.db import models

from konfera.models.abstract import KonferaModel


class Location(KonferaModel):
    title = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    street2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128)
    postcode = models.CharField(max_length=12)
    state = models.CharField(max_length=128)
    get_here = models.TextField(blank=True)
    capacity = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title
