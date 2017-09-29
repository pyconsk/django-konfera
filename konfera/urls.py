from rest_framework import routers

from konfera.views import TalkViewSet


router = routers.SimpleRouter()
router.register(r'talks', TalkViewSet)

urlpatterns = router.urls
