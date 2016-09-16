from django.db import models
from .sponsor import Sponsor
from .event import Event 

TALK_STATUS_CHOICES = (
    ('cfp', 'Call For Proposals'),
    ('draft', 'Draft'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('withdrawn', 'Withdrawn')
)

TALK_TYPE_CHOICES = (
    ('workshop', 'Workshop'),
    ('talk', 'Talk'),
)

LIGHTNING = 5
MID = 30
LONG = 45
DURATION_CHOICES = (
    (LIGHTNING, '5 min'),
    (MID, '30 min'),
    (LONG, '45 min'),
)

class Talk(models.Model):
    title = models.CharField(max_length=256)
    abstract = models.TextField()
    talktype = models.CharField(max_length=32, choices=TALK_TYPE_CHOICES)
    status = models.CharField(max_length=32, choices=TALK_STATUS_CHOICES)
    duration = models.IntegerField(choices=DURATION_CHOICES)
    primary_speaker = models.ForeignKey(Speaker, null=False, related_name='secondary_speaker')
    secondary_speaker = models.ForeignKey(Speaker, default=None, related_name='primary_speaker')
    event = models.ForeignKey(Event, null=False)

    def __str__(self):
        return self.title
