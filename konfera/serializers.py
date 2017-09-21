from collections import OrderedDict

from rest_framework import serializers

from konfera.models import Speaker, Talk, Event
from konfera.validators import event_uuid_validator


class CustomToRepresentationMixin:
    def to_representation(self, instance):
        # Default behaviour causes the following problem:
        # When object is retrieved and serialized, it contains null values,
        # after submitting the serialized data by PUT serializer shows validation
        # errors as null values are treated differently as they would be omitted.
        returned = super().to_representation(instance)
        return OrderedDict(list(filter(lambda x: x[1] is not None, returned.items())))


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
        raise NotImplementedError()  # todo: implement me!
