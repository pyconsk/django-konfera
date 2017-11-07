from rest_framework import routers

from konfera.views import TalkViewSet, AidTicketViewSet


router = routers.SimpleRouter()
router.register(r'talks', TalkViewSet)
router.register(r'tickets/aid', AidTicketViewSet)

urlpatterns = router.urls
