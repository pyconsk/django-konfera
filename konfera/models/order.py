from decimal import Decimal

from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from konfera.models.abstract import KonferaModel
from konfera.models.receipt import Receipt


class Order(KonferaModel):
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

    price = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)], default=0)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)], default=0)
    discount = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)], default=0)
    processing_fee = models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(0)], default=0)
    status = models.CharField(choices=ORDER_CHOICES, default=AWAITING, max_length=20)
    purchase_date = models.DateTimeField(auto_now_add=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    unpaid_notification_sent_at = models.DateField(blank=True, null=True)
    unpaid_notification_sent_amount = models.IntegerField(default=0)

    def __str__(self):
        return str(self.price - self.discount)

    def save(self, *args, **kwargs):
        if self.status == Order.PAID:
            if self.payment_date is None:
                self.payment_date = timezone.now()
            if self.amount_paid == 0:
                self.amount_paid = self.to_pay

        super().save(*args, **kwargs)

        try:
            self.receipt_of
        except ObjectDoesNotExist:
            receipt = Receipt(order=self, amount=self.amount_paid)
            receipt.save()

    @property
    def left_to_pay(self):
        """ Amount attendee still have to pay """
        return max(self.to_pay - self.amount_paid, Decimal(0))

    @property
    def to_pay(self):
        """ Ticket's price after discount """
        return self.price - self.discount + self.processing_fee

    @property
    def variable_symbol(self):
        return str(int(self.uuid))[:10]

    @property
    def event(self):
        if self.ticket_set.exists():
            return self.ticket_set.first().type.event

    def recalculate_ticket_price(self):
        self.price = 0
        self.discount = 0

        for ticket in self.ticket_set.all():
            self.price += ticket.type.price
            self.discount += ticket.discount_calculator()

        self.save()
