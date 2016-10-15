import datetime
import logging
from unittest.mock import patch

from django.test import TestCase
from django.test.utils import override_settings

from konfera import models
from payments import utils
from payments.models import ProcessedTransaction


def make_payment(new_data):
    data = {
        'date': datetime.date(2015, 10, 5),
        'variable_symbol': '1234',
        'transaction_id': '1234',
        'amount': 0.0,
        'currency': 'EUR',
        'comment': '',
        'executor': '',
    }
    data.update(new_data)
    return data


logging.disable(logging.WARNING)


class TestGetLastPayements(TestCase):

    @patch('django.utils.timezone.now', return_value=datetime.datetime(2016, 9, 29))
    @patch('fiobank.FioBank.period', return_value=[])
    @override_settings(FIO_BANK_TOKEN='fio_token')
    def test__get_last_payments(self, FioBankMockPeriod, timezone_mock):

        data = utils._get_last_payments()

        self.assertEqual(data, [])
        FioBankMockPeriod.assert_called_with('2016-09-26', '2016-09-29')
        timezone_mock.assert_called_once_with()


class TestGetNotProcessedPayments(TestCase):
    def test_no_processed_payment_is_available(self):
        payments = [
            make_payment({'transaction_id': '1'}),
            make_payment({'transaction_id': '2'}),
        ]
        self.assertEqual(
            list(utils._get_not_processed_payments(payments)),
            payments
        )

    def test_processed_payments_filtered(self):
        payments = [
            make_payment({'transaction_id': '1'}),
            make_payment({'transaction_id': '2'}),
            make_payment({'transaction_id': '3'}),
        ]
        ProcessedTransaction.objects.create(transaction_id='2', amount=0)
        self.assertEqual(
            list(utils._get_not_processed_payments(payments)),
            [
                make_payment({'transaction_id': '1'}),
                make_payment({'transaction_id': '3'}),
            ]
        )


class TestGetPaymentsForOrder(TestCase):
    def setUp(self):
        self.order = models.Order.objects.create(price=200, discount=0)

    def test_no_payments(self):
        payments = []
        self.assertEqual(
            list(utils._get_payments_for_order(self.order, payments)),
            []
        )

    def test_payments_for_different_orders(self):
        payments = [
            make_payment({'variable_symbol': str(self.order.pk + 7)}),
            make_payment({'variable_symbol': str(self.order.pk + 13)}),
        ]
        self.assertEqual(
            list(utils._get_payments_for_order(self.order, payments)),
            []
        )

    def test_payment_found_for_order(self):
        payments = [
            make_payment({'variable_symbol': self.order.variable_symbol}),
            make_payment({'variable_symbol': str(self.order.pk + 13)}),
        ]
        self.assertEqual(
            list(utils._get_payments_for_order(self.order, payments)),
            [make_payment({'variable_symbol': self.order.variable_symbol})]
        )

    def test_multiple_payments_found_for_order(self):
        payments = [
            make_payment({'variable_symbol': self.order.variable_symbol}),
            make_payment({'variable_symbol': str(self.order.pk + 13)}),
            make_payment({'variable_symbol': self.order.variable_symbol}),
        ]
        self.assertEqual(
            list(utils._get_payments_for_order(self.order, payments)),
            [
                make_payment({'variable_symbol': self.order.variable_symbol}),
                make_payment({'variable_symbol': self.order.variable_symbol}),
            ]
        )


class TestProcessPayment(TestCase):
    def test_attendee_paid_less(self):
        order = models.Order.objects.create(price=100, discount=10)
        payment = make_payment({'amount': 80, 'transaction_id': '7'})

        utils._process_payment(order, payment)

        self.assertEqual(order.amount_paid, 80)
        self.assertEqual(order.status, models.order.PARTLY_PAID)

    def test_attendee_paid_enough(self):
        order = models.Order.objects.create(price=100, discount=10, amount_paid=5, status=models.order.PARTLY_PAID)
        payment = make_payment({'amount': 85, 'transaction_id': '7'})

        utils._process_payment(order, payment)

        self.assertEqual(order.amount_paid, 90)
        self.assertEqual(order.status, models.order.PAID)

    def test_payment_marked_as_processed(self):
        order = models.Order.objects.create(price=100, discount=10)
        payment = make_payment({'amount': 80, 'transaction_id': '7'})

        self.assertEqual(ProcessedTransaction.objects.count(), 0)

        utils._process_payment(order, payment)

        self.assertEqual(ProcessedTransaction.objects.count(), 1)
        self.assertEqual(ProcessedTransaction.objects.all()[0].transaction_id, '7')


class TestCheckPaymentsStatus(TestCase):
    def setUp(self):
        self.order1 = models.Order.objects.create(price=200, discount=0)
        self.order2 = models.Order.objects.create(price=200, discount=7)

    @patch('payments.utils._get_last_payments', return_value=[])
    def test_no_payments_available(self, mock_api_call):
        """ FioBank doesn't have any payments - no order status should be changed """
        utils.check_payments_status()

        order1 = models.Order.objects.get(pk=self.order1.pk)
        order2 = models.Order.objects.get(pk=self.order2.pk)

        self.assertEqual(mock_api_call.call_count, 1)
        self.assertEqual(order1.status, models.order.AWAITING)
        self.assertEqual(order2.status, models.order.AWAITING)

    @patch('payments.utils._get_last_payments')
    def test_one_order_is_paid(self, mock_api_call):
        """ FioBank doesn't have a payment for order1 - order's status was changed """
        mock_api_call.return_value = [
            make_payment({'variable_symbol': self.order1.variable_symbol, 'amount': 200, 'transaction_id': '7'}),
        ]
        utils.check_payments_status()

        order1 = models.Order.objects.get(pk=self.order1.pk)
        order2 = models.Order.objects.get(pk=self.order2.pk)

        self.assertEqual(mock_api_call.call_count, 1)
        self.assertEqual(order1.status, models.order.PAID)
        self.assertEqual(order2.status, models.order.AWAITING)

    @patch('payments.utils._get_last_payments')
    def test_all_orders_are_paid(self, mock_api_call):
        mock_api_call.return_value = [
            make_payment({'variable_symbol': self.order1.variable_symbol, 'amount': 200, 'transaction_id': '7'}),
            make_payment({'variable_symbol': self.order2.variable_symbol, 'amount': 200, 'transaction_id': '8'}),
        ]

        utils.check_payments_status()

        order1 = models.Order.objects.get(pk=self.order1.pk)
        order2 = models.Order.objects.get(pk=self.order2.pk)

        self.assertEqual(mock_api_call.call_count, 1)
        self.assertEqual(order1.status, models.order.PAID)
        self.assertEqual(order2.status, models.order.PAID)

    @patch('payments.utils._get_last_payments')
    def test_order_is_paid_in_multiple_payments(self, mock_api_call):
        mock_api_call.return_value = [
            make_payment({'variable_symbol': self.order1.variable_symbol, 'amount': 150, 'transaction_id': '7'}),
            make_payment({'variable_symbol': self.order1.variable_symbol, 'amount': 50, 'transaction_id': '79'}),
            make_payment({'variable_symbol': self.order2.variable_symbol, 'amount': 30, 'transaction_id': '80'}),
        ]

        utils.check_payments_status()

        order1 = models.Order.objects.get(pk=self.order1.pk)
        order2 = models.Order.objects.get(pk=self.order2.pk)

        self.assertEqual(order1.status, models.order.PAID)
        self.assertEqual(order2.status, models.order.PARTLY_PAID)
