from django.db import models
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import KonferaModel

PLATINUM = 1
GOLD = 2
SILVER = 3
BRONZE = 4
OTHER = 5
DJANGO_GIRLS = 6

SPONSOR_TYPE = (
    (PLATINUM, _('Platinum')),
    (GOLD, _('Gold')),
    (SILVER, _('Silver')),
    (BRONZE, _('Bronze')),
    (OTHER, _('Other')),
    (DJANGO_GIRLS, _('Django girls')),
)


class Sponsor(KonferaModel):
    title = models.CharField(max_length=128)
    type = models.IntegerField(choices=SPONSOR_TYPE)
    logo = models.FileField()
    url = models.URLField()
    about_us = models.TextField(blank=True)

    def __str__(self):
        return self.title
