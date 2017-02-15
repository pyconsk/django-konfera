from decimal import Decimal
import logging
import paypalrestsdk

from django import VERSION
from django.contrib import messages
from django.http.response import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _

from konfera.models import Order
from konfera.utils import currency_round_up, generate_ga_ecommerce_context
from konfera.settings import CURRENCY
from konfera.event.views import EventOrderDetailFormView

from payments import settings
from payments.utils import _process_payment

if VERSION[1] in (8, 9):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse


logger = logging.getLogger(__name__)


paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})


class OrderPaymentView(EventOrderDetailFormView):
    template_name = 'payments/order_payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['PAYPAL_ADDITIONAL_CHARGE'] = settings.PAYPAL_ADDITIONAL_CHARGE

        return context

    def get_success_url(self):
        return reverse('konfera_payments:payment_options', kwargs={'order_uuid': self.object.order.uuid})


class OrderPaymentThanksView(OrderPaymentView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        generate_ga_ecommerce_context(self.object, context)

        return context


class PayOrderByPaypal(TemplateView):

    @staticmethod
    def calculate_processing_fee(order):
        """ Calculate the total price for order when paid by paypal """
        return order.left_to_pay * Decimal(settings.PAYPAL_ADDITIONAL_CHARGE) / Decimal('100')

    @staticmethod
    def get_paypal_url(payment):
        """ Return the PayPal URL where the user can pay for the order """
        for link in payment.links:
            if link.method == 'REDIRECT':
                return str(link.href)

        raise Exception("REDIRECT url not found when creating payment {id}".format(id=payment.id))

    @staticmethod
    def pay(request, order):
        """ Create the payment and redirect to PayPal or back to the order with an error message """
        paypal_fee = PayOrderByPaypal.calculate_processing_fee(order)
        order.processing_fee += paypal_fee
        order.save()

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": request.build_absolute_uri().split('?')[0] + '?status=success',
                "cancel_url": request.build_absolute_uri().split('?')[0] + '?status=failed',
            },
            "transactions": [
                {
                    "amount": {
                        "total": str(currency_round_up(order.left_to_pay)),
                        "currency": CURRENCY[1],
                    },
                    "description": _("Payment for {event} with variable symbol: {vs}".format(
                        event=order.event, vs=order.variable_symbol))
                },
            ]
        })

        try:
            paypal_payment = payment.create()
        except paypalrestsdk.exceptions.UnauthorizedAccess:
            payment.error = 'Client Authentication failed'
            paypal_payment = False

        if paypal_payment:
            request.session['paypal_payment_id'] = payment['id']

            try:
                return redirect(PayOrderByPaypal.get_paypal_url(payment))
            except Exception as e:
                logger.error(str(e))

        logger.error("Payment for order(pk={order}) couldn't be created! Error: {err}".format(
            order=order.pk, err=payment.error))
        messages.error(request, _('Something went wrong, try again later, or try different payment method.'))

        order.processing_fee -= paypal_fee
        order.save()

        return redirect('konfera_payments:payment_options', order_uuid=str(order.uuid))

    @staticmethod
    def success(request, order):
        """ If the payment was successful process it, otherwise show an error and log what went wrong """
        payment_id = request.session.get('paypal_payment_id')
        payment = paypalrestsdk.Payment.find(payment_id)

        payer_id = payment['payer']['payer_info']['payer_id']

        if not payment.execute({"payer_id": payer_id}):
            logger.error("Payment for order order(pk={order}) couldn't be paid! Error: {err}".format(
                order=order.pk, err=payment.error))
            return False

        payment_dict = {
            'payment_method': 'paypal',
            'amount': payment['transactions'][0]['amount']['total'],
            'currency': payment['transactions'][0]['amount']['currency'],
            'transaction_id': payment['id'],
            'variable_symbol': order.variable_symbol,
            'date': payment['create_time'].split('T')[0],
            'executor': '{first} {last} <{email}>'.format(
                first=payment['payer']['payer_info']['first_name'],
                last=payment['payer']['payer_info']['last_name'],
                email=payment['payer']['payer_info']['email']
            ),
            'comment': '',
        }

        _process_payment(order, payment_dict)
        return True

    def get(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(uuid=kwargs['order_uuid'])
        except (Order.DoesNotExist, ValueError):
            raise Http404

        if order.status == Order.PAID:
            return redirect('order_detail', order_uuid=str(order.uuid))

        status = request.GET.get('status')

        if status not in ['success', 'failed']:
            return PayOrderByPaypal.pay(request, order)

        if status == 'success' and PayOrderByPaypal.success(request, order):
            messages.success(request, _('Order successfully paid!'))
            return redirect('order_detail', order_uuid=str(order.uuid))

        order.processing_fee = 0
        order.save()

        messages.error(request, _('Something went wrong, try again later.'))
        return redirect('konfera_payments:payment_options', order_uuid=str(order.uuid))
