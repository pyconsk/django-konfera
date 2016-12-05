from datetime import timedelta
from decimal import Decimal
from smtplib import SMTPException
import requests
import logging

from django.db.models import Q
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _

from fiobank import FioBank

from konfera.models.email_template import EmailTemplate
from konfera.models import Order
from konfera.settings import CURRENCY, EMAIL_NOTIFY_BCC

from payments import settings
from payments.models import ProcessedTransaction


DATE_FORMAT = '%Y-%m-%d'


logger = logging.getLogger(__name__)


def _get_last_payments():
    """ Get list of payments for last three days from FioBank """
    client = FioBank(token=settings.FIO_BANK_TOKEN)

    today = timezone.now()
    date_from = (today - timedelta(days=settings.FIO_BANK_PROCESS_DAYS)).strftime(DATE_FORMAT)
    date_to = today.strftime(DATE_FORMAT)

    try:
        data = list(client.period(date_from, date_to))
    except (requests.exceptions.HTTPError, requests.exceptions.ConnectionError) as e:
        logger.error('{} in _get_last_payments'.format(e))
        data = []

    return data


def _get_not_processed_payments(payments):
    processed_payments = set(ProcessedTransaction.objects.values_list('transaction_id', flat=True))
    return list(filter(
        lambda payment: payment['transaction_id'] not in processed_payments,
        payments
    ))


def _get_payments_for_order(order, payments):
    return list(filter(
        lambda payment: payment['variable_symbol'] == order.variable_symbol,
        payments
    ))


def _process_payment(order, payment, verbose=0):
    """
    Process the payment
    - change the amount_paid
    - log what happend
    - add payment to ProcessedTransaction
    """

    # >>> Decimal(3.3)
    # Decimal('3.29999999999999982236431605997495353221893310546875')
    # >>> Decimal(str(3.3))
    # Decimal('3.3')
    amount = Decimal(str(payment['amount']))

    amount_to_pay = order.left_to_pay - amount

    if amount_to_pay <= order.to_pay * Decimal(settings.PAYMENT_ERROR_RATE / 100):
        order.status = Order.PAID

        msg = 'Order(id={order_id}) was paid in payment with transaction_id={transaction_id}'.format(
            order_id=order.pk, transaction_id=payment['transaction_id'])
        logger.info(msg)

        if verbose in (2, 3):
            print(msg)
    else:
        order.status = Order.PARTLY_PAID

        msg = 'Payment with transaction_id={transaction_id} for Order(id={order_id}) was found but it\'s outside ' \
              'of error rate'.format(order_id=order.pk, transaction_id=payment['transaction_id'])
        logger.warning(msg)

        if verbose in (2, 3):
            print(msg)

    order.amount_paid += amount
    order.save()

    for key in payment.keys():
        if key in ('currency', 'comment') and payment[key] is None:
            payment[key] = ''
        if not payment['executor']:
            payment['executor'] = payment['account_name']

    ProcessedTransaction.objects.create(
        transaction_id=payment['transaction_id'],
        amount=amount,
        variable_symbol=payment['variable_symbol'],
        date=payment['date'],
        executor=payment['executor'],
        currency=payment['currency'],
        comment=payment['comment'],
        method=payment.get('payment_method', 'fiobank-transfer'),
    )

    if settings.PAYMENT_PROCESS_EMAIL_NOTIFY:
        event = order.event
        template = EmailTemplate.objects.get(name='order_update_email')
        subject = _('Your ticket for {event}.'.format(event=event.title))

        for ticket in order.ticket_set.all():
            text_content = template.text_template.format(first_name=ticket.first_name, last_name=ticket.last_name,
                                                         event=event.title, price=order.price, currency=CURRENCY[1],
                                                         amount_paid=order.amount_paid, discount=order.discount,
                                                         processing_fee=order.processing_fee, status=order.status,
                                                         purchase_date=order.purchase_date,
                                                         payment_date=order.payment_date)
            html_content = template.html_template.format(first_name=ticket.first_name, last_name=ticket.last_name,
                                                         event=event.title, price=order.price,
                                                         currency=CURRENCY[1], amount_paid=order.amount_paid,
                                                         discount=order.discount, processing_fee=order.processing_fee,
                                                         status=order.status, purchase_date=order.purchase_date,
                                                         payment_date=order.payment_date)
            msg = EmailMultiAlternatives(subject, text_content, to=[ticket.email], bcc=EMAIL_NOTIFY_BCC)
            msg.attach_alternative(html_content, "text/html")

            try:
                msg.send()
            except SMTPException as e:
                logger.critical('Sending email raised an exception: %s', e)
            else:
                # increase count on email_template
                template.add_count()
                msg = 'Email template order_update_email has been send to: %s' % ticket.email
                logger.debug(msg)

                if verbose in (2, 3):
                    print(msg)


def check_payments_status(verbose=0):
    """ Process every awaiting and partly paid order """
    orders = Order.objects.filter(Q(status=Order.AWAITING) | Q(status=Order.PARTLY_PAID))

    if verbose in (2, 3):
        print('%s awaiting or partly paid orders.' % (len(orders)))

    new_payments = _get_not_processed_payments(_get_last_payments())

    if verbose:
        print('%s payments received in last %s days.' % (len(new_payments), settings.FIO_BANK_PROCESS_DAYS))

    for order in orders:
        if verbose in (2, 3):
            print('Searching order with variable symbol: %s in FIO' % order.variable_symbol, end='')

        order_payments = _get_payments_for_order(order, new_payments)

        if verbose in (2, 3):
            if order_payments:
                print(' ............ PASS')
            else:
                print(' ............ FAIL')

        for payment in order_payments:
            _process_payment(order, payment, verbose)
