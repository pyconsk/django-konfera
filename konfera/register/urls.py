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

from konfera.register import views


urlpatterns = [
    url(r'^event/(?P<slug>[\w, -]+)/ticket/volunteer/$', views.register_ticket_volunteer,
        name='ticket_registration_volunteer'),
    url(r'^event/(?P<slug>[\w, -]+)/ticket/press/$', views.register_ticket_press,
        name='ticket_registration_press'),
    url(r'^event/(?P<slug>[\w, -]+)/ticket/financial_aid/$', views.register_ticket_aid,
        name='ticket_registration_aid'),
    url(r'^event/(?P<slug>[\w, -]+)/ticket/(?P<ticket_uuid>[\w, -]+)/$', views.register_ticket,
        name='ticket_registration'),
]
