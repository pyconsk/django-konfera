from django.conf.urls import url

from konfera.event import views


urlpatterns = [
    url(r'^(?P<slug>[\w, -]+)/checkin/$', views.CheckInView.as_view(), name='check_in'),
    url(r'^(?P<slug>[\w, -]+)/checkin/(?P<order_uuid>[\w, -]+)/$', views.CheckInDetailView.as_view(), name='check_in'),
    url(r'^(?P<slug>[\w, -]+)/venue/$', views.event_venue_view, name='event_venue'),
    url(r'^(?P<slug>[\w, -]+)/speakers/$', views.event_speakers_list_view, name='event_speakers'),
    url(r'^(?P<slug>[\w, -]+)/sponsors/$', views.event_sponsors_list_view, name='event_sponsors'),
    url(r'^(?P<slug>[\w, -]+)/code-of-conduct/$', views.event_coc, name='event_coc'),
    url(r'^(?P<slug>[\w, -]+)/cfp/$', views.CFPView.as_view(), name='event_cfp_form'),
    url(r'^(?P<slug>[\w, -]+)/cfp/(?P<uuid>[\w, -]+)$', views.CFPEditView.as_view(), name='event_cfp_edit_form'),
    url(r'^(?P<slug>[\w, -]+)/schedule/$', views.schedule_redirect, name='schedule'),
    url(r'^(?P<slug>[\w, -]+)/schedule/(?P<day>[\d, -]+)$', views.ScheduleView.as_view(), name='schedule'),
    url(r'^(?P<slug>[\w, -]+)/tickets/$', views.event_public_tickets, name='event_tickets'),
    url(r'^(?P<slug>[\w, -]+)/$', views.event_details_view, name='event_details'),
    url(r'^order/(?P<order_uuid>[\w, -]+)/$', views.EventOrderDetailView.as_view(), name='order_detail'),
    url(r'^order/(?P<order_uuid>[\w, -]+)/thanks/$', views.EventOrderDetailThanksView.as_view(),
        name='order_detail_thanks'),
    url(r'^order/(?P<order_uuid>[\w, -]+)/edit/$', views.EventOrderDetailFormView.as_view(), name='order_detail_edit'),
    url(r'^order/(?P<order_uuid>[\w, -]+)/pdf/$', views.EventOrderDetailPDFView.as_view(), name='order_detail_pdf'),
    url(r'^(?P<slug>[\w, -]+)/about_us/$', views.event_about_us, name='event_about_us'),
]
