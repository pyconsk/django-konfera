from decimal import Decimal
from unittest.mock import patch

from django.test import TestCase
from django.test.utils import override_settings

from konfera import models
from payments import utils


class TestIsOrderPaid(TestCase):
    def setUp(self):
        self.order = models.Order.objects.create(price=200, discount=0)

    def test_order_paid(self):
        """ Attendee paid for ticket - good variable_symbol and amount """
        payments = [{'variable_symbol': str(self.order.pk), 'amount': 200}]
        self.assertTrue(utils._is_order_paid(self.order, payments))

    def test_paid_less(self):
        """ Attendee didn't paid enough """
        payments = [{'variable_symbol': str(self.order.pk), 'amount': 42}]
        self.assertFalse(utils._is_order_paid(self.order, payments))

    def test_variable_symbol_notfound(self):
        """ Atendee didn't paid yet - no matching variable_symbol """
        payments = [{'variable_symbol': str(self.order.pk), 'amount': 200}]
        order = models.Order.objects.create(price=200, discount=7)
        self.assertFalse(utils._is_order_paid(order, payments))

    def test_discounted_order_paid(self):
        order = models.Order.objects.create(price=200, discount=70)
        payments = [{'variable_symbol': str(order.pk), 'amount': 130}]
        self.assertTrue(utils._is_order_paid(order, payments))

    @override_settings(PAYMENT_ERROR_RATE=Decimal('0.01'))
    def test_error_rate(self):
        payments = [{'variable_symbol': str(self.order.pk), 'amount': 198}]
        self.assertTrue(utils._is_order_paid(self.order, payments))

        payments = [{'variable_symbol': str(self.order.pk), 'amount': 197.99}]
        self.assertFalse(utils._is_order_paid(self.order, payments))


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
        mock_api_call.return_value = [{'variable_symbol': str(self.order1.pk), 'amount': 200}]
        utils.check_payments_status()

        order1 = models.Order.objects.get(pk=self.order1.pk)
        order2 = models.Order.objects.get(pk=self.order2.pk)

        self.assertEqual(mock_api_call.call_count, 1)
        self.assertEqual(order1.status, models.order.PAID)
        self.assertEqual(order2.status, models.order.AWAITING)

    @patch('payments.utils._get_last_payments')
    def test_all_orders_are_paid(self, mock_api_call):
        mock_api_call.return_value = [
            {'variable_symbol': str(self.order1.pk), 'amount': 200},
            {'variable_symbol': str(self.order2.pk), 'amount': 200},
        ]
        utils.check_payments_status()

        order1 = models.Order.objects.get(pk=self.order1.pk)
        order2 = models.Order.objects.get(pk=self.order2.pk)

        self.assertEqual(mock_api_call.call_count, 1)
        self.assertEqual(order1.status, models.order.PAID)
        self.assertEqual(order2.status, models.order.PAID)


class TestGetLastPayements(TestCase):

    @patch('fiobank.FioBank.period', return_value=[])
    @override_settings(FIO_BANK_TOKEN='fio_token')
    def test__get_last_payments(self, FioBankMockPeriod):

        data = utils._get_last_payments()

        self.assertEqual(data, [])
        FioBankMockPeriod.assert_called_with('2016-09-26', '2016-09-29')  # todo: freeze time
