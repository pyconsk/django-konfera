from django.db import models
from django.utils.translation import ugettext_lazy as _

from konfera.models.countries import COUNTRIES
from konfera.models.abstract import KonferaModel

TITLE_UNSET = 'none'
COUNTRY_DEFAULT = 'SK'

TITLE_CHOICES = (
    (TITLE_UNSET, ''),
    ('mr', _('Mr.')),
    ('ms', _('Ms.')),
)


class Speaker(KonferaModel):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    title = models.CharField(
        choices=TITLE_CHOICES,
        max_length=4,
        default=TITLE_UNSET
    )
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=64, blank=True)
    bio = models.TextField(blank=True)
    url = models.URLField(blank=True)
    social_url = models.URLField(blank=True)
    country = models.CharField(
        choices=COUNTRIES,
        max_length=2,
        default=COUNTRY_DEFAULT
    )
    sponsor = models.ForeignKey('Sponsor', blank=True, null=True, related_name='sponsored_speakers')

    def __str__(self):
        return '{title} {first_name} {last_name}'.format(
            title=dict(TITLE_CHOICES)[self.title],
            first_name=self.first_name,
            last_name=self.last_name
        ).strip()
