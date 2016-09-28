from django.db import models


class Location(models.Model):
    title = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    street2 = models.CharField(max_length=128, blank=True)
    city = models.CharField(max_length=128)
    postcode = models.CharField(max_length=12)
    state = models.CharField(max_length=128)
    capacity = models.IntegerField()

    def __str__(self):
        return self.title
