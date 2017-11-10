from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from konfera.models.abstract import FromToModel


class EventManager(models.Manager):
    def public(self):
        return self.get_queryset().filter(status=Event.PUBLIC).select_related('location')


class Event(FromToModel):
    DRAFT = 'draft'
    PUBLIC = 'public'
    PRIVATE = 'private'

    EVENT_STATUS_CHOICES = (
        (DRAFT, _('Draft')),
        (PUBLIC, _('Public')),
        (PRIVATE, _('Private')),
    )

    title = models.CharField(verbose_name=_('Event name'), max_length=128)
    slug = models.SlugField(verbose_name=_('Event url'), max_length=128, unique=True,
                            help_text=_('Slug field, relative URL to the event.'))
    status = models.CharField(choices=EVENT_STATUS_CHOICES, max_length=20, default=DRAFT)
    organizer = models.ForeignKey('Organizer', on_delete=models.deletion.SET_NULL,
                                  related_name='organized_events', null=True, )
    cfp_end = models.DateTimeField(verbose_name=_('Call for proposals deadline'), null=True, blank=True)
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
        if not self.cfp_end or self.cfp_end > self.date_to or timezone.now() > self.cfp_end:
            return False
        return True

    def clean(self):
        if self.cfp_end and self.cfp_end > self.date_to:
            raise ValidationError(_('CFP deadline should be before the event end.'))

        super(Event, self).clean()

    def save(self, *args, **kwargs):
        self.clean()
        super(Event, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('event_details', kwargs={'slug': self.slug})


Event._meta.get_field('date_from').blank = False
Event._meta.get_field('date_from').verbose_name = _('Event beginning')
Event._meta.get_field('date_to').blank = False
Event._meta.get_field('date_to').verbose_name = _('Event end')
