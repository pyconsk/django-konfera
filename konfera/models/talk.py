from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

TALK_STATUS = (
    ('cfp', 'Call For Proposals'),
    ('draft', 'Draft'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('withdrawn', 'Withdrawn')
)

TALK_TYPE = (
    ('talk', 'Talk'),
    ('workshop', 'Workshop'),
)

TALK_DURATION = (
    (5, '5 min'),
    (30, '30 min'),
    (45, '45 min'),
)


class Talk(models.Model):
    title = models.CharField(max_length=256)
    abstract = models.TextField(help_text=_('Abstract will be published in the schedule.'))
    type = models.CharField(choices=TALK_TYPE, max_length=32)
    status = models.CharField(choices=TALK_STATUS, max_length=32)
    duration = models.IntegerField(choices=TALK_DURATION, help_text=_('Talk duration in minutes.'))
    primary_speaker = models.ForeignKey(
        'Speaker',
        related_name='primary_speaker_talks',
        verbose_name=_('Primary speaker'),
    )
    secondary_speaker = models.ForeignKey(
        'Speaker',
        related_name='secondary_speaker_talks',
        verbose_name=_('Secondary speaker'),
        blank=True,
        null=True,
    )
    event = models.ForeignKey('Event')

    def __str__(self):
        return self.title

    def clean(self):
        if hasattr(self, 'primary_speaker') and hasattr(self, 'secondary_speaker') \
                and self.primary_speaker == self.secondary_speaker:
            msg = _('%(primary)s have to be different than %(secondary)s.') % {
                'primary': self._meta.get_field('primary_speaker').verbose_name,
                'secondary': self._meta.get_field('secondary_speaker').verbose_name
            }

            raise ValidationError({'primary_speaker': msg, 'secondary_speaker': msg})
