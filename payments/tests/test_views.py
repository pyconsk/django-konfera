from decimal import Decimal
from unittest.mock import patch

from django.http import HttpResponse
from django.test import TestCase
from django.urls import reverse

from konfera.models import Order
from payments.views import PayOrderByPaypal
from payments.tests.utils import custom_override_settings


class TestPaymentOptions(TestCase):
    pass


class TestPayOrderByPaypal(TestCase):

    # Tests for .get_paypal_price()

    @custom_override_settings(PAYPAL_ADDITIONAL_CHARGE=0)
    def test_get_paypal_price(self):
        order = Order(price=200, discount=100, amount_paid=50)
        self.assertEqual(PayOrderByPaypal.get_paypal_price(order), Decimal('50'))

    @custom_override_settings(PAYPAL_ADDITIONAL_CHARGE=7)
    def test_get_paypal_price2(self):
        order = Order(price=200, discount=100, amount_paid=50)
        self.assertEqual(PayOrderByPaypal.get_paypal_price(order), Decimal('53.5'))

    # Tests for .get()

    def test_get_invalid_order(self):
        url = reverse('konfera_payments:paypal_button_url', kwargs={'order_uuid': 7})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_redirect_for_paid_order(self):
        order = Order.objects.create(price=0, status=Order.PAID)
        url = reverse('konfera_payments:paypal_button_url', kwargs={'order_uuid': order.uuid})

        response = self.client.get(url)

        expected_redirect_url = reverse('order_details', kwargs={'order_uuid': order.uuid})
        self.assertRedirects(response, expected_redirect_url)

    @patch('payments.views.PayOrderByPaypal.pay', return_value=HttpResponse())
    def test_redirect_to_paypal(self, pay_method_mock):
        order = Order.objects.create(price=100, status=Order.AWAITING)
        url = reverse('konfera_payments:paypal_button_url', kwargs={'order_uuid': order.uuid})

        self.client.get(url)

        self.assertTrue(pay_method_mock.called)

    def test_get_redirect_after_paypal_callback_failed(self):
        order = Order.objects.create(price=100, status=Order.AWAITING)
        url = reverse('konfera_payments:paypal_button_url', kwargs={'order_uuid': order.uuid}) + '?status=failed'

        response = self.client.get(url)

        expected_redirect_url = reverse('order_details', kwargs={'order_uuid': order.uuid})
        self.assertRedirects(response, expected_redirect_url)

    @patch('payments.views.PayOrderByPaypal.success', return_value=True)
    def test_get_redirect_after_paypal_callback_success(self, success_method_mock):
        order = Order.objects.create(price=100, status=Order.AWAITING)
        url = reverse('konfera_payments:paypal_button_url', kwargs={'order_uuid': order.uuid}) + '?status=success'

        response = self.client.get(url)

        self.assertTrue(success_method_mock.called)

        expected_redirect_url = reverse('order_details', kwargs={'order_uuid': order.uuid})
        self.assertRedirects(response, expected_redirect_url)

    # todo: test: get_paypal_url, pay, success
