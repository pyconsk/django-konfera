from django.db import models


TITLE_UNSET = 'none'

TITLE_CHOICES = (
    (TITLE_UNSET, ''),
    ('mr', 'Mr.'),
    ('ms', 'Ms.'),
)


class Speaker(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    title = models.CharField(
        choices=TITLE_CHOICES,
        max_length=4,
        default=TITLE_UNSET
    )
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=64)
    bio = models.TextField()
    url = models.URLField(blank=True, null=True)
    social_url = models.URLField(blank=True, null=True)
    country = models.CharField(max_length=64)
    sponsor = models.ForeignKey('Sponsor', blank=True, null=True)

    def __str__(self):
        return '{title} {first_name} {last_name}'.format(
            title=dict(TITLE_CHOICES)[self.title],
            first_name=self.first_name,
            last_name=self.last_name
        ).strip()
