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
    url(r'^event/(?P<slug>[\w, -]+)/publicticket/(?P<ticket_uuid>[\w, -]+)/$', views.public_registration,
        name='event_public_registration'),
    url(r'^event/(?P<slug>[\w, -]+)/privateticket/(?P<ticket_uuid>[\w, -]+)/$', views.private_registration,
        name='event_private_registration'),
]
