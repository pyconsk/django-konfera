from rest_framework import viewsets

from konfera.models import Speaker
from konfera.serializers import SpeakerSerializer


class SpeakerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
