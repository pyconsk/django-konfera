from django.db import models
from django.utils.translation import ugettext_lazy as _

from konfera.models.countries import COUNTRIES
from konfera.models.abstract import KonferaModel


class Speaker(KonferaModel):
    TITLE_UNSET = 'none'
    TITLE_MR = 'mr'
    TITLE_MS = 'ms'
    TITLE_MX = 'mx'
    COUNTRY_DEFAULT = 'SK'

    TITLE_CHOICES = (
        (TITLE_UNSET, ''),
        (TITLE_MR, _('Mr.')),
        (TITLE_MS, _('Ms.')),
        (TITLE_MX, _('Mx.')),
    )

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
    image = models.ImageField(upload_to='speaker/', blank=True)

    def __str__(self):
        return '{first_name} {last_name}'.format(
            first_name=self.first_name,
            last_name=self.last_name
        ).strip()
