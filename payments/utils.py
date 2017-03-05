from datetime import timedelta
from decimal import Decimal
import requests
import logging

from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django import VERSION

from fiobank import FioBank

from konfera.models import Order
from konfera.settings import (CURRENCY, EMAIL_NOTIFY_BCC, SITE_URL,
                              UNPAID_ORDER_NOTIFICATION_REPEAT, UNPAID_ORDER_NOTIFICATION_REPEAT_DELAY)
from konfera.utils import send_email

from payments import settings
from payments.models import ProcessedTransaction

if VERSION[1] in (8, 9):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse


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
        subject = _('Your ticket for {event}.'.format(event=event.title))
        template_name = 'order_update_email'

        for ticket in order.ticket_set.all():
            formatting_dict = {
                'first_name': ticket.first_name,
                'last_name': ticket.last_name,
                'event': event.title,
                'price': order.price,
                'currency': CURRENCY[1],
                'amount_paid': order.amount_paid,
                'discount': order.discount,
                'processing_fee': order.processing_fee,
                'status': order.status,
                'purchase_date': order.purchase_date,
                'payment_date': order.payment_date
            }
            addresses = {'to': [ticket.email], 'bcc': EMAIL_NOTIFY_BCC}
            send_email(addresses, subject, template_name, formatting_dict=formatting_dict)


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


def get_full_order_url(order):
    return SITE_URL + reverse('order_detail', kwargs={'order_uuid': order.uuid})


def get_unpaid_orders_print_results(overdue, verbose):
    orders_no = 0
    tickets_no = 0
    for order in Order.get_unpaid_orders(overdue=overdue):
        orders_no += 1
        tickets_no += len(order.ticket_set.all())

        if verbose == 3:
            print('Order variable symbol: %s, has number of tickets %s, notified %s time(s) last at %s. ' % (
                order.variable_symbol, len(order.ticket_set.all()), order.unpaid_notification_sent_amount,
                order.unpaid_notification_sent_at
            ), end='')
            print('Tickets: ', end='')
            for ticket in order.ticket_set.all():
                print('%s %s, ' % (ticket.first_name, ticket.last_name), end='')
            print('')

        if verbose == 2:
            print('Order variable symbol: %s, has number of tickets %s, notified %s time(s) last at %s' % (
                order.variable_symbol, len(order.ticket_set.all()), order.unpaid_notification_sent_amount,
                order.unpaid_notification_sent_at
            ))

    return orders_no, tickets_no


def show_overdue_orders(verbose=0):
    """
    Display all users who has orders overdue.
    """
    return get_unpaid_orders_print_results(True, verbose)


def show_unpaid_orders(verbose=0):
    """
    Display all users who has no paid orders yet.
    """
    return get_unpaid_orders_print_results(False, verbose)


def email_overdue_orders(verbose=0):
    """
    Mark overdue orders as EXPIRED and send email notifications
    """
    overdue_orders = Order.get_unpaid_orders(overdue=True)
    template_name = 'expired_order_notification'

    for order in overdue_orders:
        subject = 'Your order for {event} has expired.'.format(event=order.event.title)
        order_url = get_full_order_url(order)

        for ticket in order.ticket_set.all():
            content_data = {
                'first_name': ticket.first_name,
                'last_name': ticket.last_name,
                'event': order.event.title,
                'order_url': order_url,
            }
            addresses = {'to': [ticket.email], 'bcc': EMAIL_NOTIFY_BCC}
            send_email(addresses, subject, template_name, content_data)
            msg = 'Email template expired_order_notification has been send to: %s' % ticket.email

            if verbose > 2:
                print(msg)
            logger.debug(msg)

            order.unpaid_notification_sent_at = timezone.now()
            order.unpaid_notification_sent_amount += 1

        order.status = Order.EXPIRED
        order.save()


def email_unpaid_orders(verbose=0):
    """
    Send email to all users who has unpaid orders.
    """
    email_overdue_orders(verbose=verbose)

    # notify the rest
    orders = Order.get_unpaid_orders()
    template_name = 'unpaid_order_notification'

    for order in orders:
        subject = 'Your order for {event} haven\'t been paid yet.'.format(event=order.event.title)
        order_url = get_full_order_url(order)

        for ticket in order.ticket_set.all():
            content_data = {
                'first_name': ticket.first_name,
                'last_name': ticket.last_name,
                'event': order.event.title,
                'order_url': order_url,
            }
            addresses = {'to': [ticket.email], 'bcc': EMAIL_NOTIFY_BCC}
            send_email(addresses, subject, template_name, content_data)
            msg = 'Email template unpaid_order_notification has been send to: %s' % ticket.email

            if verbose > 2:
                print(msg)
            logger.debug(msg)

            order.unpaid_notification_sent_at = timezone.now()
            order.unpaid_notification_sent_amount += 1

        order.save()
