from django.db import models

class Receipt(models.Model):
    title = models.CharField(max_length=128)
    street = models.CharField(max_length=128)
    street2 = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    postcode = models.CharField(max_length=12)
    state = models.CharField(max_length=128)
    companyid = models.CharField(max_length=32)
    taxid = models.CharField(max_length=32)
    vatid = models.CharField(max_length=32)
    amount = models.FloatField()

    def __str__(self):
        return "Receipt: {} ({})".format(self.title, self.amount)

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

