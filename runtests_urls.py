from django.conf.urls import url, include


urlpatterns = [
    url(r'', include('konfera.urls')),
    url(r'', include('payments.urls', namespace='konfera_payments')),
]
