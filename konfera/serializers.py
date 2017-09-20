from rest_framework import serializers

from konfera.models import Speaker


class SpeakerSerializer(serializers.ModelSerializer):
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
