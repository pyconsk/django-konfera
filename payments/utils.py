from datetime import timedelta
from decimal import Decimal

from django.db.models import Q
from django.conf import settings
from django.utils import timezone

from fiobank import FioBank

from konfera.models import Order
from konfera.models.order import AWAITING, PAID, PARTLY_PAID
from payments.models import ProcessedTransation


DATE_FORMAT = '%Y-%m-%d'


def _get_last_payments():
    """ Get list of payments for last three days from FioBank """
    client = FioBank(token=settings.FIO_BANK_TOKEN)

    today = timezone.now()
    date_from = (today - timedelta(days=3)).strftime(DATE_FORMAT)
    date_to = today.strftime(DATE_FORMAT)
    return list(client.period(date_from, date_to))


def _get_payments_for_order(order, payments):
    return filter(
        lambda payment: payment['variable_symbol'] == str(order.pk),  # todo: change order.pk to variable_symbol
        payments
    )


def _process_payment(order, payment):
    """
    Process the payment
    - change the amount_paid
    - send the order's status to attendee by email
    - log what happend
    - add payment to ProcessedTransation
    """
    amount_to_pay = order.left_to_pay - payment['amount']

    if amount_to_pay <= order.to_pay * Decimal(settings.PAYMENT_ERROR_RATE / 100):
        # todo: log + email
        order.status = PAID
    else:
        # todo: log + email
        order.status = PARTLY_PAID

    order.amount_paid += payment['amount']
    order.save()
    ProcessedTransation.objects.create(transaction_id=payment['transaction_id'])


def check_payments_status():
    """ For every awaiting and partly paid order check whether there is a new payment """

    # Filter not processed payments
    payments = _get_last_payments()
    processed_payments = set(ProcessedTransation.objects.values_list('transaction_id', flat=True))  # todo: select only the new one (last 3 days)
    new_payments = filter(
        lambda payment: payment['transaction_id'] not in processed_payments,
        payments
    )

    orders = Order.objects.filter(Q(status=AWAITING) | Q(status=PARTLY_PAID))

    # Process the payments
    for order in orders:
        order_payments = _get_payments_for_order(order, new_payments)

        for payment in order_payments:
            _process_payment(order, payment)
