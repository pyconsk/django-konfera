from django.conf.urls import url, include
from rest_framework import routers

from .views import EventViewSet, TalkViewSet, AidTicketViewSet, EventTicketTypesList, EventTicketTypeDetail, \
    EventTalksList, EventSpeakersList

router = routers.SimpleRouter()
router.register(r'events', EventViewSet)
router.register(r'talks', TalkViewSet)
router.register(r'tickets/aid', AidTicketViewSet)


# urlpatterns = router.urls

urlpatterns = [
    url(r'^', include(router.urls)),
    url('^event/(?P<slug>.+)/ticket-types/$', EventTicketTypesList.as_view()),
    url('^event/(?P<slug>.+)/ticket-types/(?P<uuid>.+)/$', EventTicketTypeDetail.as_view()),
    url('^event/(?P<slug>.+)/talks/', EventTalksList.as_view()),
    url('^event/(?P<slug>.+)/speakers/', EventSpeakersList.as_view())
]
