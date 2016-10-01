from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


AWAITING = 'awaiting_payment'
PAID = 'paid'
PARTLY_PAID = 'partly_paid'
EXPIRED = 'expired'
CANCELLED = 'cancelled'

ORDER_CHOICES = (
    (AWAITING, _('Awaiting payment')),
    (PARTLY_PAID, _('Partly paid')),
    (PAID, _('Paid')),
    (EXPIRED, _('Expired')),
    (CANCELLED, _('Cancelled')),
)


class Order(models.Model):
    price = models.DecimalField(decimal_places=2, max_digits=12)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=12, default=0)
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

    @property
    def left_to_pay(self):
        """ Amount attendee still have to pay """
        return max(self.to_pay - self.amount_paid, Decimal(0))

    @property
    def to_pay(self):
        """ Ticket's price after discount """
        return self.price - self.discount

    @property
    def variable_symbol(self):
        return str(self.pk)  # todo: change to something better
