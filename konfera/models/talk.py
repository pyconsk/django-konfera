from django.db import models


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
    abstract = models.TextField()
    type = models.CharField(choices=TALK_TYPE, max_length=32)
    status = models.CharField(choices=TALK_STATUS, max_length=32)
    duration = models.IntegerField(choices=TALK_DURATION)
    primary_speaker = models.ForeignKey('Speaker', related_name='secondary_speaker')
    secondary_speaker = models.ForeignKey('Speaker', related_name='primary_speaker', blank=True, null=True)
    event = models.ForeignKey('Event')

    def __str__(self):
        return self.title
