from django.db import models

# Create your models here.


class Location(models.Model):
    
    title = models.CharField(max_length = 128)
    street = models.CharField(max_length = 128)
    street2 = models.CharField(max_length = 128)
    city = models.CharField(max_length = 128)
    postcode = models.CharField(max_length = 12)
    state = models.CharField(max_length = 128)
    capacity = models.IntegerField()

    def __str__(self):
        return "Location: %s %s %s %s %s %s %s" % self.title, self.street, self.street2, self.city, self.postcode, self.state, self.capacity

