from django.db import models
from konfera.models import Speaker, Event

TALK_TYPE = (
    ('talk', 'Talk'),
    ('workshop', 'Workshop'),
)

TALK_STATUS = (
    ('cfp', 'Call for prop'),
    ('draft', 'Draft'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('withdrawn', 'Withdrawn'),
)

TALK_DURATION = (
    (30, '30 min'),
    (45, '45 min'),
)


class Talk(models.Model):
    title = models.CharField(max_length=256)
    abstract = models.TextField()
    type = models.CharField(choices=TALK_TYPE)
    status = models.CharField(choices=TALK_STATUS)
    duration = models.CharField(choices=TALK_DURATION)
    primary_speaker = models.ForeignKey(Speaker, null=False)
    secondary_speaker = models.ForeignKey(Speaker, default=None)
    event = models.ForeignKey(Event, null=False)

    def __str__(self):
        return self.title
