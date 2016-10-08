from datetime import timedelta
from decimal import Decimal
import logging

from django.db.models import Q
from django.conf import settings
from django.utils import timezone

from fiobank import FioBank

from konfera.models import Order
from konfera.models.order import AWAITING, PAID, PARTLY_PAID
from payments.models import ProcessedTransation


DATE_FORMAT = '%Y-%m-%d'


logger = logging.getLogger(__name__)


def _get_last_payments():
    """ Get list of payments for last three days from FioBank """
    client = FioBank(token=settings.FIO_BANK_TOKEN)

    today = timezone.now()
    date_from = (today - timedelta(days=3)).strftime(DATE_FORMAT)
    date_to = today.strftime(DATE_FORMAT)
    return list(client.period(date_from, date_to))


def _get_not_processed_payments(payments):
    processed_payments = set(ProcessedTransation.objects.values_list('transaction_id', flat=True))
    return list(filter(
        lambda payment: payment['transaction_id'] not in processed_payments,
        payments
    ))


def _get_payments_for_order(order, payments):
    return list(filter(
        lambda payment: payment['variable_symbol'] == order.variable_symbol,
        payments
    ))


def _process_payment(order, payment):
    """
    Process the payment
    - change the amount_paid
    - log what happend
    - add payment to ProcessedTransation
    """
    amount_to_pay = order.left_to_pay - payment['amount']

    if amount_to_pay <= order.to_pay * Decimal(settings.PAYMENT_ERROR_RATE / 100):
        order.status = PAID

        msg = 'Order(id={order_id}) was paid in payment with transaction_id={transaction_id}'.format(
            order_id=order.pk, transaction_id=payment['transaction_id'])
        logger.warning(msg)
    else:
        order.status = PARTLY_PAID

        msg = 'Payment with transaction_id={transaction_id} for Order(id={order_id}) was found but it\'s outside ' \
              'of error rate'.format(order_id=order.pk, transaction_id=payment['transaction_id'])
        logger.warning(msg)

    order.amount_paid += payment['amount']
    order.save()
    ProcessedTransation.objects.create(transaction_id=payment['transaction_id'])


def check_payments_status():
    """ Process every awaiting and partly paid order """

    orders = Order.objects.filter(Q(status=AWAITING) | Q(status=PARTLY_PAID))
    new_payments = _get_not_processed_payments(_get_last_payments())

    for order in orders:

        order_payments = _get_payments_for_order(order, new_payments)
        for payment in order_payments:
            _process_payment(order, payment)
