from django.conf.urls import url

from konfera.event import views


urlpatterns = [
    url(r'^(?P<event_slug>[\w, -]+)/speakers/$', views.event_speakers_list_view, name='event_speakers'),
    url(r'^(?P<event_slug>[\w, -]+)/sponsors/$', views.event_sponsors_list_view, name='event_sponsors'),
    url(r'^(?P<event_slug>[\w, -]+)/cfp/$', views.cfp_form_view, name='event_cfp_form'),
    url(r'^(?P<event_slug>[\w, -]+)/$', views.event_details_view, name='event_details'),
    url(r'^$', views.event_list, name='events'),
]
