from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^(?P<pk>\d+)/ticket/(?P<ticket_uuid>[\w, -]+)/$', views.ShowFormForTicket.as_view()),
    url(r'^df/', include('dynamic_forms.urls', namespace='dynamic_forms')),
]
