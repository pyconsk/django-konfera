import logging
import paypalrestsdk

from django.contrib import messages
from django.http.response import Http404
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.utils.translation import ugettext as _

from konfera.models import Order


logger = logging.getLogger(__name__)

# todo: move constants to settings
paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "xxx",
  "client_secret": "xxx"
})


class PaymentOptions(TemplateView):
    template_name = 'payments/order_payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            context['order'] = Order.objects.get(uuid=kwargs['order_uuid'])
        except (Order.DoesNotExist, ValueError):
            raise Http404

        return context


class PayOrderByPaypal(TemplateView):

    def pay(self, request, order):
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
                        "total": str(order.to_pay),  # todo: increase by 2% or so
                        "currency": "EUR",  # todo: make it configurable
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
            logger.error("Payment for order(pk={order}) couldn't be created! Error: {err}".format(order=order.pk, err=payment.error))
            raise AssertionError  # todo: show an error message instead?

    def success(self, request, order):
        payment_id = request.session.get('paypal_payment_id')
        payment = paypalrestsdk.Payment.find(payment_id)

        payer_id = payment['payer']['payer_info']['payer_id']

        if not payment.execute({"payer_id": payer_id}):
            logger.error("Payment for order order(pk={order}) couldn't be paid! Error: {err}".format(order=order.pk, err=payment.error))
            return False

        from .utils import _process_payment

        payment_dict = {
            'payment_method': 'paypal',  # todo: save it to DB!
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

        if status not in ['success', 'failed'] and order.left_to_pay > 0:
            return self.pay(request, order)

        if status == 'success' and self.success(request, order):
            messages.success(request, _('Order successfully paid!'))
        else:
            messages.warning(request, _('Something went wrong, try again later.'))

        return redirect('order_details', order_uuid=str(order.uuid))
