from konfera.models.countries import COUNTRIES
from django.db import models
from konfera.models.abstract import KonferaModel


class Organizer(KonferaModel):
    COUNTRY_DEFAULT = 'SK'

    title = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    street2 = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    postcode = models.CharField(max_length=12)
    country = models.CharField(
        choices=COUNTRIES,
        max_length=2,
        default=COUNTRY_DEFAULT)
    company_id = models.CharField(max_length=32)
    tax_id = models.CharField(max_length=32)
    vat_id = models.CharField(max_length=32)
    about_us = models.TextField(blank=True)

    def __str__(self):
        return self.title
