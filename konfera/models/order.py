from datetime import timedelta
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from konfera.models.abstract import KonferaModel
from konfera.models.receipt import Receipt
from konfera.settings import UNPAID_ORDER_NOTIFICATION_REPEAT, UNPAID_ORDER_NOTIFICATION_REPEAT_DELAY


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

        if self.status == Order.CANCELLED:
            self.price = 0
            self.discount = 0

            for ticket in self.ticket_set.all():
                ticket.status = ticket.CANCELLED
                ticket.save()

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
            if ticket.status != ticket.CANCELLED:
                self.price += ticket.type.price
                self.discount += ticket.discount_calculator()

        self.save()

    @staticmethod
    def get_unpaid_orders(overdue=False):
        deadline = timezone.now() - timedelta(days=UNPAID_ORDER_NOTIFICATION_REPEAT_DELAY)
        orders = Order.objects.filter(Q(status=Order.AWAITING) | Q(status=Order.PARTLY_PAID))
        orders = orders.filter((Q(unpaid_notification_sent_amount=0) & Q(date_created__lt=deadline)) |
                               Q(unpaid_notification_sent_at__lt=deadline))
        if overdue:
            return orders.filter(unpaid_notification_sent_amount=UNPAID_ORDER_NOTIFICATION_REPEAT)
        return orders.filter(unpaid_notification_sent_amount__lt=UNPAID_ORDER_NOTIFICATION_REPEAT)

    def expire_overdue_orders(self):
        self.get_unpaid_orders(overdue=True)
