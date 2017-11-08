from rest_framework import routers

from konfera.views import EventViewSet, TalkViewSet, AidTicketViewSet


router = routers.SimpleRouter()
router.register(r'events', EventViewSet)
router.register(r'talks', TalkViewSet)
router.register(r'tickets/aid', AidTicketViewSet)

urlpatterns = router.urls
