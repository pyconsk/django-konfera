from decimal import Decimal
import logging
import paypalrestsdk

from django.contrib import messages
from django.http.response import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _

from konfera.models import Order

from payments import settings


logger = logging.getLogger(__name__)


paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET,
})


class PaymentOptions(TemplateView):
    template_name = 'payments/order_payment.html'

    def get_order(self, uuid):
        try:
            return Order.objects.get(uuid=uuid)
        except (Order.DoesNotExist, ValueError):
            raise Http404

    def dispatch(self, request, *args, **kwargs):

        order = self.get_order(kwargs['order_uuid'])
        if order.status == Order.PAID:
            return redirect('order_details', order_uuid=str(order.uuid))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = self.get_order(kwargs['order_uuid'])

        return context


class PayOrderByPaypal(TemplateView):

    def pay(self, request, order):
        paypal_additional_charge = order.left_to_pay * Decimal(settings.PAYPAL_ADDITIONAL_CHARGE) / Decimal('100')
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
                        "total": str(order.left_to_pay + paypal_additional_charge),
                        "currency": settings.PAYPAL_CURRENCY,
                    },
                    "description": _("Payment for order with variable symbol: {vs}".format(vs=order.variable_symbol))
                },
            ]
        })

        if payment.create():
            approval_url = None
            for link in payment.links:
                if link.method == 'REDIRECT':
                    approval_url = str(link.href)
                    break

            request.session['paypal_payment_id'] = payment['id']

            return redirect(approval_url)
        else:
            logger.error("Payment for order(pk={order}) couldn't be created! Error: {err}".format(
                order=order.pk, err=payment.error))
            messages.error(request, _('Something went wrong, try again later.'))
            return redirect('konfera_payments:payment_options', order_uuid=str(order.uuid))

    def success(self, request, order):
        payment_id = request.session.get('paypal_payment_id')
        payment = paypalrestsdk.Payment.find(payment_id)

        payer_id = payment['payer']['payer_info']['payer_id']

        if not payment.execute({"payer_id": payer_id}):
            logger.error("Payment for order order(pk={order}) couldn't be paid! Error: {err}".format(
                order=order.pk, err=payment.error))
            return False

        from .utils import _process_payment

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
        status = request.GET.get('status')

        try:
            order = Order.objects.get(uuid=kwargs['order_uuid'])
        except (Order.DoesNotExist, ValueError):
            raise Http404

        if order.status == Order.PAID:
            return redirect('order_details', order_uuid=str(order.uuid))

        if status not in ['success', 'failed'] and order.left_to_pay > 0:
            return self.pay(request, order)

        if status == 'success' and self.success(request, order):
            messages.success(request, _('Order successfully paid!'))
        else:
            messages.error(request, _('Something went wrong, try again later.'))

        return redirect('order_details', order_uuid=str(order.uuid))
