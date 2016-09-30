from datetime import timedelta
from decimal import Decimal

from django.db.models import Q
from django.conf import settings
from django.utils import timezone

from fiobank import FioBank

from konfera.models import Order
from konfera.models.order import AWAITING, PAID, PARTLY_PAID


DATE_FORMAT = '%Y-%m-%d'


def _get_payment_for_order(order, payments):
    for payment in payments:

        if payment['variable_symbol'] == str(order.pk):  # todo: variable symbol not .pk
            return payment

    return None


def _get_last_payments():
    """ Get list of payments for last three days from FioBank """
    client = FioBank(token=settings.FIO_BANK_TOKEN)

    today = timezone.now()
    date_from = (today - timedelta(days=3)).strftime(DATE_FORMAT)
    date_to = today.strftime(DATE_FORMAT)

    return list(client.period(date_from, date_to))


def _process_payment(order, payment):
    amount_to_pay = order.left_to_pay - payment['amount']

    if amount_to_pay <= order.to_pay * Decimal(settings.PAYMENT_ERROR_RATE / 100):
        # todo: log + email
        order.status = PAID
    else:
        # todo: log + email
        order.status = PARTLY_PAID

    order.amount_paid += payment['amount']
    order.save()


def check_payments_status():
    """ Check whether order was already paid. If so, change the order's status to PAID """
    payments = _get_last_payments()
    orders = Order.objects.filter(Q(status=AWAITING) | Q(status=PARTLY_PAID))

    for order in orders:
        payment = _get_payment_for_order(order, payments)

        if payment:
            _process_payment(order, payment)
