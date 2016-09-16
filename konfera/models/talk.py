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
    ('workshop', 'workshop'),
    ('talk', 'talk'),
)

LIGHTNING = 5
MID = 30
LONG = 45
DURATION_CHOICES = (
    (LIGHTNING, 5),
    (MID, 30),
    (LONG, 45),
)

class Talk(models.Model):
    title = models.CharField(max_length=256)
    abstract = models.TextField()
    talktype = models.CharField(max_length=32, choices=TALK_TYPE_CHOICES)
    status = models.CharField(max_length=32, choices=TALK_STATUS_CHOICES)
    duration = models.IntegerField(choices=DURATION_CHOICES)
    primary_speaker = models.ForeignKey(Speaker)
    secondary_speaker = models.ForeignKey(Speaker)
    event = models.ForeignKey(Event)

