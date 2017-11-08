from collections import OrderedDict

from rest_framework import serializers

from konfera.models import Speaker, Talk, Event, Ticket, TicketType
from konfera.validators import event_uuid_validator, aid_ticket_type_uuid_validator


class CustomToRepresentationMixin:
    def to_representation(self, instance):
        # Default behaviour causes the following problem:
        # When object is retrieved and serialized, it contains null values,
        # after submitting the serialized data by PUT serializer shows validation
        # errors as null values are treated differently as they would be omitted.
        returned = super().to_representation(instance)
        return OrderedDict(list(filter(lambda x: x[1] is not None, returned.items())))


class AidTicketSerializer(
    CustomToRepresentationMixin,
    serializers.ModelSerializer
):
    type_uuid = serializers.UUIDField(validators=[aid_ticket_type_uuid_validator])
    description = serializers.CharField(required=True)

    class Meta:
        model = Ticket
        fields = [
            'type_uuid',
            'title',
            'first_name',
            'last_name',
            'email',
            'phone',
            'description'
        ]

    def create(self, validated_data):
        tt_uuid = validated_data.pop('type_uuid')

        ticket = Ticket(**validated_data)
        ticket.type = TicketType.objects.get(uuid=tt_uuid)
        ticket.status = Ticket.REQUESTED
        ticket.save()

        return ticket


class SpeakerSerializer(
    CustomToRepresentationMixin,
    serializers.ModelSerializer
):
    class Meta:
        model = Speaker
        fields = [
            'title',
            'first_name',
            'last_name',
            'email',
            'phone',
            'bio',
            'url',
            'social_url',
            'country',
            'image',
        ]


class TalkSerializer(
    CustomToRepresentationMixin,
    serializers.ModelSerializer
):
    event_uuid = serializers.UUIDField(validators=[event_uuid_validator])
    primary_speaker = SpeakerSerializer()
    secondary_speaker = SpeakerSerializer(required=False)

    class Meta:
        fields = [
            'event_uuid',
            'title',
            'abstract',
            'type',
            'language',
            'duration',
            'flag',
            'primary_speaker',
            'secondary_speaker',
        ]
        model = Talk

    def create(self, validated_data):
        event_uuid = validated_data.pop('event_uuid')
        primary_speaker_data = validated_data.pop('primary_speaker')
        secondary_speaker_data = validated_data.pop('secondary_speaker', None)

        talk = Talk(**validated_data)
        talk.event = Event.objects.get(uuid=event_uuid)
        talk.primary_speaker = Speaker.objects.create(**primary_speaker_data)
        if secondary_speaker_data:
            talk.secondary_speaker = Speaker.objects.create(**secondary_speaker_data)

        talk.save()
        return talk

    def update(self, instance, validated_data):

        # Update normal fields
        for key in ('title', 'abstract', 'type', 'language', 'duration'):
            value = validated_data.pop(key) if key in validated_data else getattr(instance, key)
            setattr(instance, key, value)

        # Update speakers
        for key in ('primary_speaker', 'secondary_speaker'):
            speaker = SpeakerSerializer(
                instance=getattr(instance, key),
                data=validated_data.pop(key)
            )
            speaker.is_valid()
            setattr(instance, key, speaker.save())

        instance.save()
        return instance
