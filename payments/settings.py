from django.conf import settings


FIO_BANK_TOKEN = getattr(settings, 'FIO_BANK_TOKEN', 'token')
PAYMENT_ERROR_RATE = getattr(settings, 'PAYMENT_ERROR_RATE', 0)

PAYPAL_CURRENCY = getattr(settings, 'PAYPAL_CURRENCY', 'EUR')
PAYPAL_MODE = getattr(settings, 'PAYPAL_MODE', 'sandbox')
PAYPAL_CLIENT_ID = getattr(settings, 'PAYPAL_CLIENT_ID', 'client_id')
PAYPAL_CLIENT_SECRET = getattr(settings, 'PAYPAL_CLIENT_SECRET', 'secret')
