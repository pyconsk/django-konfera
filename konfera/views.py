from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from konfera.models import Event, Speaker, Talk, Ticket, TicketType
from konfera.serializers import EventSerializer, SpeakerSerializer, TalkSerializer, TicketTypeListSerializer, \
    TicketTypeDetailSerializer, AidTicketSerializer


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = 'slug'
    queryset = Event.objects.filter(status=Event.PUBLIC).order_by('date_from', 'date_to', 'title')
    serializer_class = EventSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = ('title', 'date_from', 'date_to', 'cfp_end')
    filter_fields = ('title',)


class EventTicketTypesList(generics.ListAPIView):
    serializer_class = TicketTypeListSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        return TicketType.objects.filter(event__slug=slug, accessibility=TicketType.PUBLIC)


class EventTicketTypeDetail(generics.RetrieveAPIView):
    lookup_field = 'uuid'
    serializer_class = TicketTypeDetailSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        return TicketType.objects.filter(event__slug=slug)


class EventTalksList(generics.ListAPIView):
    serializer_class = TalkSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = ('title', 'type', 'language', 'flag', 'primary_speaker__last_name')
    filter_fields = ('type', 'language', 'flag', 'primary_speaker__last_name')

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Talk.objects.filter(event__slug=slug).filter(status=Talk.PUBLISHED).order_by('title')


class EventSpeakersList(generics.ListAPIView):
    serializer_class = SpeakerSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    ordering_fields = ('last_name', 'first_name', 'country')
    filter_fields = ('last_name', 'first_name', 'country',)

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Speaker.objects.filter(primary_speaker_talks__event__status=Event.PUBLIC).filter(
            Q(primary_speaker_talks__event__slug=slug) | Q(secondary_speaker_talks__event__slug=slug)).filter(
            Q(primary_speaker_talks__status=Talk.PUBLISHED) | Q(secondary_speaker_talks__status=Talk.PUBLISHED))\
            .distinct('first_name', 'last_name').order_by('last_name', 'first_name')


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
