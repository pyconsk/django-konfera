from django.db import models


ORDER_CHOICES = (
    ('awaiting_payment', 'awaiting payment'),
    ('paid', 'paid'),
    ('expired', 'expired'),
    ('cancelled', 'cancelled'),
)


class Order(models.Model):
    price = models.DecimalField()
    discount = models.IntegerField()
    status = models.CharField(choices=ORDER_CHOICES, max_length=256)
    purchase_date = models.DateTimeField()
    payment_date = models.DateTimeField()
