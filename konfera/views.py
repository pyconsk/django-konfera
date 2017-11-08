from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from konfera.models import Speaker, Talk, Ticket
from konfera.serializers import SpeakerSerializer, TalkSerializer, AidTicketSerializer


class AidTicketViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'uuid'
    queryset = Ticket.objects.all()
    serializer_class = AidTicketSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response({'key': obj.uuid}, status=status.HTTP_201_CREATED, headers=headers)


class SpeakerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer


class TalkViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = 'uuid'
    queryset = Talk.objects.all()
    serializer_class = TalkSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response({'key': obj.uuid}, status=status.HTTP_201_CREATED, headers=headers)
