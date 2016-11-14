from datetime import datetime
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import FromToModel


class EventManager(models.Manager):
    def published(self):
        return self.get_queryset().filter(status=Event.PUBLISHED).select_related('location')


class Event(FromToModel):
    CONFERENCE = 'conference'
    MEETUP = 'meetup'

    EVENT_TYPE_CHOICES = (
        (CONFERENCE, _('Conference')),
        (MEETUP, _('Meetup')),
    )

    DRAFT = 'draft'
    PUBLISHED = 'published'
    PRIVATE = 'private'
    EXPIRED = 'expired'

    EVENT_STATUS_CHOICES = (
        (DRAFT, _('Draft')),
        (PUBLISHED, _('Published')),
        (PRIVATE, _('Private')),
        (EXPIRED, _('Expired')),
    )

    title = models.CharField(verbose_name=_('Event name'), max_length=128)
    slug = models.SlugField(verbose_name=_('Event url'), max_length=128, unique=True,
                            help_text=_('Slug field, relative URL to the event.'))
    description = models.TextField(blank=True)
    event_type = models.CharField(choices=EVENT_TYPE_CHOICES, max_length=20)
    status = models.CharField(choices=EVENT_STATUS_CHOICES, max_length=20)
    location = models.ForeignKey('Location', related_name='events')
    sponsors = models.ManyToManyField('Sponsor', blank=True, related_name='sponsored_events')
    footer_text = models.TextField(blank=True)
    analytics = models.TextField(blank=True)

    cfp_allowed = models.BooleanField(default=True, help_text=_('Is it allowed to submit talk proposals?'))
    cfp_end = models.DateTimeField(verbose_name=_('CFP deadline'),
                                   default=datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc),
                                   help_text=_('Call for proposals deadline.'))
    contact_email = models.EmailField(verbose_name=_('E-mail'), blank=True,
                                      help_text=_('Publicly displayed email to contact organizers.'))
    coc = models.TextField(verbose_name=_('Code of Conduct'), blank=True)
    coc_phone = models.CharField(verbose_name=_('Code of Conduct contact'),
                                 help_text=_('Publicly displayed phone to contact organizers.'),
                                 max_length=20, blank=True)
    coc_phone2 = models.CharField(verbose_name=_('Code of Conduct contact 2'),
                                  help_text=_('Publicly displayed phone to contact organizers.'),
                                  max_length=20, blank=True)

    objects = EventManager()

    class Meta:
        ordering = ('-date_from',)

    def __str__(self):
        return self.title

    @property
    def duration(self):
        return (self.date_to - self.date_from).days + 1

    @property
    def cfp_open(self):
        return self.cfp_allowed and self.cfp_end >= datetime.now(tz=timezone.utc)

    def clean(self):
        if self.cfp_allowed and self.cfp_end == datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc):
            raise ValidationError(_('CFP deadline has to be defined if CFP is allowed.'))
        # at this point cfp_end is defined
        if self.cfp_end.date() >= self.date_from:
            raise ValidationError(_('CFP deadline should be before the event starts.'))
        super(Event, self).clean()

Event._meta.get_field('date_from').blank = False
Event._meta.get_field('date_from').verbose_name = _('Event beginning')
Event._meta.get_field('date_to').blank = False
Event._meta.get_field('date_to').verbose_name = _('Event end')
