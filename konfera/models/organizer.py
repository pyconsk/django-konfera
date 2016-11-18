from django.db import models
from konfera.models.abstract import KonferaModel
from konfera.models.countries import COUNTRIES


class Organizer(KonferaModel):
    COUNTRY_DEFAULT = 'SK'

    title = models.CharField(max_length=128)
    street = models.CharField(max_length=128, blank=True)
    street2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128, blank=True)
    postcode = models.CharField(max_length=12, blank=True)
    country = models.CharField(choices=COUNTRIES, max_length=2, default=COUNTRY_DEFAULT)
    company_id = models.CharField(max_length=32, blank=True)
    tax_id = models.CharField(max_length=32, blank=True)
    vat_id = models.CharField(max_length=32, blank=True)
    about_us = models.TextField(blank=True)

    def __str__(self):
        return self.title
