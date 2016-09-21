from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError


class FromToModel(models.Model):

    class Meta:
        abstract = True

    date_from = models.DateTimeField(verbose_name=_('Beginning'))
    date_to = models.DateTimeField(verbose_name=_('End'))

    def clean(self):
        if self.date_from >= self.date_to:
            msg = _('%(date_from)s have to be before %(date_to)s') % {
                'date_from': self._meta.get_field('date_from').verbose_name,
                'date_to': self._meta.get_field('date_to').verbose_name
            }
            raise ValidationError({'date_from': msg, 'date_to': msg})
