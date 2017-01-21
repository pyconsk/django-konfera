from decimal import Decimal
from unittest.mock import patch

from django.http import HttpResponse
from django.test import TestCase

from konfera.models import Order
from payments.views import PayOrderByPaypal
from payments.tests.utils import custom_override_settings

from django import VERSION

if VERSION[1] in (8, 9):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse


class TestPaymentOptions(TestCase):
    pass


class TestPayOrderByPaypal(TestCase):

    # Tests for .get_paypal_price()
    def setUp(self):
        self.order_await = Order.objects.create(price=100, discount=0, status=Order.AWAITING)

    @custom_override_settings(PAYPAL_ADDITIONAL_CHARGE=0)
    def test_get_paypal_price(self):
        order = Order(price=200, discount=100, amount_paid=50)
        order.processing_fee = PayOrderByPaypal.calculate_processing_fee(order)
        self.assertEqual(order.processing_fee, Decimal('0'))
        self.assertEqual(order.left_to_pay, Decimal('50'))

    @custom_override_settings(PAYPAL_ADDITIONAL_CHARGE=5)
    def test_get_paypal_price2(self):
        order = Order(price=200, discount=100, amount_paid=50)
        order.processing_fee = PayOrderByPaypal.calculate_processing_fee(order)
        self.assertEqual(order.processing_fee, Decimal('2.5'))
        self.assertEqual(order.left_to_pay, Decimal('52.5'))

    # Tests for .get()

    def test_get_invalid_order(self):
        url = reverse('konfera_payments:paypal_button_url', kwargs={'order_uuid': 7})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_get_redirect_for_paid_order(self):
        order = Order.objects.create(price=0, status=Order.PAID)
        url = reverse('konfera_payments:paypal_button_url', kwargs={'order_uuid': order.uuid})

        response = self.client.get(url)

        expected_redirect_url = reverse('order_detail', kwargs={'order_uuid': order.uuid})
        self.assertRedirects(response, expected_redirect_url)

    @patch('payments.views.PayOrderByPaypal.pay', return_value=HttpResponse())
    def test_redirect_to_paypal(self, pay_method_mock):
        url = reverse('konfera_payments:paypal_button_url', kwargs={'order_uuid': self.order_await.uuid})
        self.client.get(url)
        self.assertTrue(pay_method_mock.called)

    def test_get_redirect_after_paypal_callback_failed(self):
        url = reverse('konfera_payments:paypal_button_url',
                      kwargs={'order_uuid': self.order_await.uuid}) + '?status=failed'

        response = self.client.get(url)
        expected_redirect_url = reverse('konfera_payments:payment_options',
                                        kwargs={'order_uuid': str(self.order_await.uuid)})
        self.assertRedirects(response, expected_redirect_url)

    @patch('payments.views.PayOrderByPaypal.success', return_value=True)
    def test_get_redirect_after_paypal_callback_success(self, success_method_mock):
        url = reverse('konfera_payments:paypal_button_url',
                      kwargs={'order_uuid': self.order_await.uuid}) + '?status=success'

        response = self.client.get(url)
        self.assertTrue(success_method_mock.called)

        expected_redirect_url = reverse('order_detail', kwargs={'order_uuid': self.order_await.uuid})
        self.assertRedirects(response, expected_redirect_url)

    def test_metatags_noindex_nofollow(self):
        url = reverse('konfera_payments:payment_options', kwargs={'order_uuid': self.order_await.uuid})
        response = self.client.get(url)

        # self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertEqual('<meta name="robots" content="noindex,nofollow" />' in content, True)
        self.assertEqual('<meta name="googlebot" content="nosnippet,noarchive" />' in content, True)

    # todo: test: get_paypal_url, pay, success
