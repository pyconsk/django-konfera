import paypalrestsdk

from django.http.response import Http404
from django.http.request import HttpRequest

from django.shortcuts import redirect
from django.views.generic import TemplateView

from konfera.models import Order


paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "ccccc",
  "client_secret": "xxxxx"
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
                        "total": str(order.to_pay),  # todo: increase by 2%
                        "currency": "EUR",  # todo: set currency
                    },
                    "description": "Payment for order {vs}".format(vs=order.variable_symbol)
                },
            ]
        })

        if payment.create():
            approval_url = None
            for link in payment.links:
                if link.method == 'REDIRECT':
                    approval_url = str(link.href)
                    break

            return redirect(approval_url)
        else:
            # todo. log error (payment.error) & raise a 500
            pass

    def success(self, request):
        payment_id = request.session.get('paypal_payment_id')
        payment = paypalrestsdk.Payment.find(payment_id)

        payer_id = payment['payer']['payer_info']['payer_id']

        if payment.execute({"payer_id": payer_id}) and payment['state'] == 'approved':
            # todo: log it was successful, pay the order
            pass
        else:
            # todo: log error!
            self.template_name = 'payments/order_payment_failed.html'

    def get(self, request, *args, **kwargs):
        status = request.GET.get('status')

        try:
            order = Order.objects.get(uuid=kwargs['order_uuid'])
        except (Order.DoesNotExist, ValueError):
            raise Http404

        if status == 'success':
            self.template_name = 'payments/order_payment_success.html'
            self.success(request)
            return super().get(request, *args, **kwargs)
        elif status == 'failed':
            self.template_name = 'payments/order_payment_failed.html'
            return super().get(request, *args, **kwargs)

        if order.left_to_pay > 0:
            return self.pay(request, order)

        return redirect('/')
