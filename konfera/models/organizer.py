from django.db import models
from konfera.models.abstract import AddressModel
from konfera.models.countries import COUNTRIES


class Organizer(AddressModel):
    COUNTRY_DEFAULT = 'SK'

    title = models.CharField(max_length=128)
    company_id = models.CharField(max_length=32, blank=True)
    tax_id = models.CharField(max_length=32, blank=True)
    vat_id = models.CharField(max_length=32, blank=True)
    about_us = models.TextField(blank=True)

    def __str__(self):
        return self.title
