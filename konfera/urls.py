from rest_framework import routers

from konfera.views import SpeakerViewSet


router = routers.SimpleRouter()
router.register(r'speakers', SpeakerViewSet)

urlpatterns = router.urls
