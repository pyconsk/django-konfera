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
from django.conf.urls import url, include
from konfera import views
from konfera.models import event

urlpatterns = [
    url(r'^events/', include('konfera.event.urls'), name='event_list'),
    url(r'^register/', include('konfera.register.urls')),
    url(r'^meetups/', views.EventsByTypeListView.as_view(template_name='konfera/meetups.html',
                                                         event_type=event.MEETUP), name='list_all_meetups'),
    url(r'^conferences/', views.EventsByTypeListView.as_view(template_name='konfera/conferences.html',
                                                             event_type=event.CONFERENCE), name='conference_list'),
]
