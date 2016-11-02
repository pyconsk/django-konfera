from django.db import models

from konfera.models.abstract import KonferaModel
from konfera.models.countries import COUNTRIES


class Location(KonferaModel):
    STATE_DEFAULT = 'SK'

    title = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    street2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128)
    postcode = models.CharField(max_length=12)
    state = models.CharField(
        choices=COUNTRIES,
        max_length=2,
        default=STATE_DEFAULT)
    get_here = models.TextField(blank=True)
    capacity = models.IntegerField(blank=True, null=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.title
