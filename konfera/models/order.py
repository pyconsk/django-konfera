from django.db import models

ORDER_CHOICES = (
    ('awaiting_payment', 'awaiting payment'),
    ('paid', 'paid'),
    ('expired', 'expired'),
    ('cancelled', 'cancelled'),
)


class Order(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=12)
    discount = models.IntegerField()
    status = models.CharField(choices=ORDER_CHOICES, max_length=256)
    purchase_date = models.DateTimeField()
    payment_date = models.DateTimeField()

    def __str__(self):
        return self.title
