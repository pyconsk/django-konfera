from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


EVENT_TYPE_CHOICES = (
    ('conference', _('Conference')),
    ('meetup', _('Meetup')),
)

EVENT_STATUS_CHOICES = (
    ('draft', _('Draft')),
    ('published', _('Published')),
    ('expired', _('Expired')),
)


class Event(models.Model):
    title = models.CharField(verbose_name=_('Event name'), max_length=128)
    slug = models.SlugField(verbose_name=_('Event url'), help_text=_('Slug field, relative URL to the event.'))
    description = models.TextField()
    date_from = models.DateTimeField(verbose_name=_('Event begging'))
    date_to = models.DateTimeField(verbose_name=_('Event end'))
    event_type = models.CharField(choices=EVENT_TYPE_CHOICES, max_length=20)
    status = models.CharField(choices=EVENT_STATUS_CHOICES, max_length=20)
    location = models.ForeignKey('Location')
    sponsors = models.ManyToManyField('Sponsor', blank=True, related_name='sponsored_events')

    def __str__(self):
        return self.title

    def clean(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('%(date_from)s have to be before %(date_to)s'),
                                  params={'date_from': self._meta.get_field('date_from').verbose_name,
                                          'date_to': self._meta.get_field('date_to').verbose_name},
                                  )
