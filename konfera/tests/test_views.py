from konfera.serializers import SpeakerSerializer
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from konfera.models import Speaker, Talk, Event


class CFPViewSetTest(APITestCase):
    def setUp(self):
        self.event = mommy.make(Event)

    def test_post_valid_data_saves_object_and_returns_uuid(self):
        data = {
            'event_uuid': self.event.uuid,
            'title': 'Modern web development and python',
            'abstract': 'Rest API and another stuff',
            'primary_speaker': {
                'first_name': 'Zoltan',
                'last_name': 'Onody',
                'email': 'zoltan@example.com',
            },
            'secondary_speaker': {
                'first_name': 'Richard',
                'last_name': 'Kellner',
                'email': 'richard@example.com',
            },
        }
        response = self.client.post('/talks/', data, format='json')

        talks = Talk.objects.all()
        speakers = Speaker.objects.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(talks.count(), 1)
        self.assertEqual(speakers.count(), 2)
        self.assertEqual(response.data, {'key': talks.first().uuid})

    def test_invalid_data_shows_validation_erros(self):
        response = self.client.post('/talks/', {'primary_speaker': {}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            'event_uuid': ['This field is required.'],
            'abstract': ['This field is required.'],
            'title': ['This field is required.'],
            'primary_speaker': {
                'first_name': ['This field is required.'],
                'last_name': ['This field is required.'],
                'email': ['This field is required.'],
            }
        })

    def test_get_cfp_by_uuid(self):  # todo: fix this test
        talk = mommy.make(Talk, event=self.event)
        response = self.client.get('/talks/' + str(talk.uuid) + '/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)
        self.assertEqual(response.data, {
            'event_uuid': talk.event_uuid,
            'title': talk.title,
            'abstract': talk.abstract,
            'type': talk.type,
            'language': talk.language,
            'duration': talk.duration,
            'primary_speaker': SpeakerSerializer(talk.primary_speaker).data,
        })
