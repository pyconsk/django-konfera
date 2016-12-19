from decimal import Decimal
import logging
import paypalrestsdk

from django.contrib import messages
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _

from konfera.models import Order
from konfera.utils import update_order_status_context, update_event_context, currency_round_up
from konfera.event.forms import ReceiptForm
from konfera.settings import CURRENCY

from payments import settings
from payments.utils import _process_payment


logger = logging.getLogger(__name__)


paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})


def order_payment(request, order_uuid):
    order = get_object_or_404(Order, uuid=order_uuid)
    context = dict()

    if order.status == Order.PAID:
        return redirect('order_detail', order_uuid=str(order.uuid))

    if order.status == Order.AWAITING:
        context['form'] = form = ReceiptForm(request.POST or None, instance=order.receipt_of)

        if form.is_valid():
            form.save()
            messages.success(request, _('Your order details has been updated.'))

    if order.event:
        update_event_context(order.event, context, show_sponsors=False)

    context['PAYPAL_ADDITIONAL_CHARGE'] = settings.PAYPAL_ADDITIONAL_CHARGE
    context['order'] = order
    update_order_status_context(order.status, context)

    return render(request=request, template_name='payments/order_payment.html', context=context)


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
        else:
            order.processing_fee = 0
            order.save()

            messages.error(request, _('Something went wrong, try again later.'))

        return redirect('order_detail', order_uuid=str(order.uuid))
