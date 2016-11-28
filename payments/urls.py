from django.conf.urls import url

from payments import views


urlpatterns = [
    url(r'^order/(?P<order_uuid>[\w, -]+)/payment$', views.order_payment, name='payment_options'),
    url(r'^order/(?P<order_uuid>[\w, -]+)/paypal$', views.PayOrderByPaypal.as_view(), name='paypal_button_url'),
]
