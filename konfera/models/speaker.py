from django.db import models
from konfera.models import Sponsor


class Speaker(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=64)
    bio = models.TextField()
    url = models.URLField()
    social_url = models.URLField()
    country = models.CharField(max_length=64)
    sponsor = models.ForeignKey(Sponsor, default=None)

    def __str__(self):
        return self.title
