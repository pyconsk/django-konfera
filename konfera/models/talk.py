from django.db import models


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
    type = models.CharField(choices=TALK_TYPE, max_length=32)
    status = models.CharField(choices=TALK_STATUS, max_length=32)
    duration = models.CharField(choices=TALK_DURATION, max_length=32)
    primary_speaker = models.ForeignKey('Speaker', null=False, related_name='secondary_speaker')
    secondary_speaker = models.ForeignKey('Speaker', default=None, related_name='primary_speaker')
    event = models.ForeignKey('Event', null=False)

    def __str__(self):
        return self.title
