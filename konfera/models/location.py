from django.db import models

from konfera.models.abstract import AddressModel


class Location(AddressModel):
    title = models.CharField(max_length=128)
    get_here = models.TextField(blank=True)
    capacity = models.IntegerField(blank=True, null=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.title
