from django.db import models


SPONSOR_TYPE = (
    (1, 'Platinum'),
    (2, 'Gold'),
    (3, 'Silver'),
    (4, 'Bronze'),
    (5, 'Other'),
    (6, 'Django girls'),
)


class Sponsor(models.Model):
    title = models.CharField(max_length=128)
    type = models.IntegerField(choices=SPONSOR_TYPE)
    logo = models.FileField()
    url = models.URLField()
    about_us = models.TextField()

    def __str__(self):
        return self.title
