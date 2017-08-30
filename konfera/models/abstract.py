import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from konfera.models.countries import COUNTRIES


class KonferaModel(models.Model):

    class Meta:
        abstract = True

    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    date_created = models.DateTimeField(verbose_name=_('Created'), auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name=_('Last modified'), auto_now=True)


class FromToModel(KonferaModel):

    class Meta:
        abstract = True

    date_from = models.DateTimeField(verbose_name=_('Available from'), blank=True)
    date_to = models.DateTimeField(verbose_name=_('Available to'), blank=True)

    def clean(self):
        if self.date_from and not self.date_to:
            msg = _('%(date_to)s have not been set.') % {
                'date_to': self._meta.get_field('date_to').verbose_name
            }
            raise ValidationError({'date_to': msg})

        if self.date_to and not self.date_from:
            msg = _('%(date_from)s have not been set.') % {
                'date_from': self._meta.get_field('date_from').verbose_name,
            }
            raise ValidationError({'date_from': msg})

        if self.date_from and self.date_to and self.date_from >= self.date_to:
            msg = _('%(date_from)s have to be before %(date_to)s.') % {
                'date_from': self._meta.get_field('date_from').verbose_name,
                'date_to': self._meta.get_field('date_to').verbose_name
            }
            raise ValidationError({'date_from': msg, 'date_to': msg})


class AddressModel(KonferaModel):
    COUNTRY_DEFAULT = 'SK'

    class Meta:
        abstract = True

    street = models.CharField(max_length=128, blank=True)
    street2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128, blank=True)
    postcode = models.CharField(max_length=12, blank=True)
    state = models.CharField(max_length=128, blank=True)
    country = models.CharField(choices=COUNTRIES, max_length=2, default=COUNTRY_DEFAULT)
