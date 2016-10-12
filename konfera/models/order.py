from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import KonferaModel


class Order(KonferaModel):
    ORDER_CHOICES = (
        ('awaiting_payment', _('Awaiting payment')),
        ('paid', _('Partly paid')),
        ('partly_paid', _('Paid')),
        ('expired', _('Expired')),
        ('cancelled', _('Cancelled')),
    )
    price = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)])
    amount_paid = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)], default=0)
    discount = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)], default=0)
    status = models.CharField(choices=ORDER_CHOICES, default='awaiting_payment', max_length=20)
    purchase_date = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return str(self.price - self.discount)

    def save(self, *args, **kwargs):
        if self.status == 'paid' and self.payment_date is None:
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
