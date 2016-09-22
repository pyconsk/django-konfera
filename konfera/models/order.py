from django.db import models
from django.utils.translation import ugettext_lazy as _


ORDER_CHOICES = (
    ('awaiting_payment', _('Awaiting payment')),
    ('paid', _('Paid')),
    ('expired', _('Expired')),
    ('cancelled', _('Cancelled')),
)


class Order(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=12)
    discount = models.DecimalField(decimal_places=2, max_digits=12)
    status = models.CharField(choices=ORDER_CHOICES, max_length=256)
    purchase_date = models.DateTimeField()
    payment_date = models.DateTimeField()

    def __str__(self):
        return str(self.price - self.discount)
