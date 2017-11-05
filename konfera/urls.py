from rest_framework import routers

from konfera.views import TalkViewSet, TicketViewSet


router = routers.SimpleRouter()
router.register(r'talks', TalkViewSet)
router.register(r'aid', TicketViewSet)

urlpatterns = router.urls
