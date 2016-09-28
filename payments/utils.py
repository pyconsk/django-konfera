from datetime import datetime, timedelta

from django.conf import settings
from fiobank import FioBank

from konfera.models import Order
from konfera.models.order import AWAITING, PAID


DATE_FORMAT = '%Y-%m-%d'


def _is_order_paid(order, payments):
    """ Check whether order was already paid """
    for payment in payments:
        if payment['variable_symbol'] == str(order.pk) and payment['amount'] >= (order.price - order.discount):
            return True

    return False


def _get_last_payments():
    """ Get list of payments for last three days from FioBank """
    client = FioBank(token=settings.FIO_BANK_TOKEN)

    today = datetime.today()
    date_from = (today - timedelta(days=3)).strftime(DATE_FORMAT)
    date_to = today.strftime(DATE_FORMAT)

    return list(client.period(date_from, date_to))


def check_payments_status():
    """ Check whether order was already paid. If so, change the order's status to PAID """
    payments = _get_last_payments()
    orders = Order.objects.filter(status=AWAITING)

    for order in orders:
        if _is_order_paid(order, payments):
            order.status = PAID
            order.save()
