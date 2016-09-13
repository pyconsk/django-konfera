from django.db import models


class Location(models.Model):

    title = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    street2 = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    postcode = models.CharField(max_length=12)
    state = models.CharField(max_length=128)
    capacity = models.IntegerField()

    def __str__(self):
        return "Location: {} {} {} {} {} {} {}".format(
            self.title, self.street, self.street2, self.city,
            self.postcode, self.state, self.capacity)


class Sponsor(models.Model):
    pass


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


