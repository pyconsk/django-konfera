from django.db import models
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import FromToModel


EVENT_TYPE_CHOICES = (
    ('conference', _('Conference')),
    ('meetup', _('Meetup')),
)

DRAFT = 'draft'
PUBLISHED = 'published'
EXPIRED = 'expired'

EVENT_STATUS_CHOICES = (
    (DRAFT, _('Draft')),
    (PUBLISHED, _('Published')),
    (EXPIRED, _('Expired')),
)


class EventManager(models.Manager):
    def published(self):
        return self.get_queryset().filter(status=PUBLISHED)


class Event(FromToModel):
    title = models.CharField(verbose_name=_('Event name'), max_length=128)
    slug = models.SlugField(verbose_name=_('Event url'), help_text=_('Slug field, relative URL to the event.'))
    description = models.TextField()
    event_type = models.CharField(choices=EVENT_TYPE_CHOICES, max_length=20)
    status = models.CharField(choices=EVENT_STATUS_CHOICES, max_length=20)
    location = models.ForeignKey('Location')
    sponsors = models.ManyToManyField('Sponsor', blank=True, related_name='sponsored_events')

    objects = EventManager()

    def __str__(self):
        return self.title


Event._meta.get_field('date_from').blank = False
Event._meta.get_field('date_from').verbose_name = _('Event beginning')
Event._meta.get_field('date_to').blank = False
Event._meta.get_field('date_to').verbose_name = _('Event end')
