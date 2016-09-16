from django.db import models

EVENT_TYPE_CHOICES = (
    ('conference', 'Conference'),
    ('meetup', 'Meetup'),
)

EVENT_STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('expired', 'Expired'),
)


class Event(models.Model):
    title = models.CharField(max_length=128)
    slug = models.SlugField()
    description = models.TextField()
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    event_type = models.CharField(choices=EVENT_TYPE_CHOICES, max_length=20)
    status = models.CharField(choices=EVENT_STATUS_CHOICES, max_length=20)
    location = models.ForeignKey('Location')
    sponsors = models.ManyToManyField('Sponsor', blank=True, related_name='sponsored_events')

    def __str__(self):
        return self.title
