from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


AWAITING = 'awaiting_payment'
PAID = 'paid'

ORDER_CHOICES = (
    (AWAITING, _('Awaiting payment')),
    (PAID, _('Paid')),
    ('expired', _('Expired')),
    ('cancelled', _('Cancelled')),
)


class Order(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=12)
    discount = models.DecimalField(decimal_places=2, max_digits=12)
    status = models.CharField(choices=ORDER_CHOICES, default=AWAITING, max_length=20)
    purchase_date = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.price - self.discount)

    def save(self, *args, **kwargs):
        if self.status == PAID and self.payment_date is None:
            self.payment_date = timezone.now()

        super().save(*args, **kwargs)
