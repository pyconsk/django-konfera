"""django_konfera URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from konfera import views

urlpatterns = [
    url(r'^event/(?P<event_slug>[\w, -]+)/speakers/$', views.event_speakers_list_view,
        name='event_speakers'),
    url(r'^event/(?P<event_slug>[\w, -]+)/sponsors/$', views.event_sponsors_list_view,
        name='event_sponsors'),
    url(r'^event/add_speaker/$', views.add_speaker_view, name='add_speaker_form'),
    url(r'^event/add_talk/$', views.add_talk_view, name='add_talk_form'),
    url(r'^event/$', views.event_list, name='events'),
]
