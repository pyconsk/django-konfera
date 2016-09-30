import datetime
from unittest.mock import patch

from django.test import TestCase
from django.test.utils import override_settings

from konfera import models
from payments import utils


# todo:
# - test _get_payment_for_order
# - test _process_payment


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

    # todo: add test - status is changed for both awating/party paid if a new payments is made


class TestGetLastPayements(TestCase):

    @patch('django.utils.timezone.now', return_value=datetime.datetime(2016, 9, 29))
    @patch('fiobank.FioBank.period', return_value=[])
    @override_settings(FIO_BANK_TOKEN='fio_token')
    def test__get_last_payments(self, FioBankMockPeriod, timezone_mock):

        data = utils._get_last_payments()

        self.assertEqual(data, [])
        FioBankMockPeriod.assert_called_with('2016-09-26', '2016-09-29')
        timezone_mock.assert_called_once_with()
