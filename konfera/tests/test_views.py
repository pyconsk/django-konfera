import datetime
import json

from model_mommy import mommy
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from konfera.models import Speaker, Talk, Event, TicketType, Ticket

now = timezone.now()
hour = datetime.timedelta(hours=1)
day = datetime.timedelta(days=1)
earlier = now - 8 * hour
later = now + 8 * hour
past = now - 3 * day
future = now + 3 * day


class AidTicketViewSetTest(APITestCase):
    def setUp(self):
        self.url = '/tickets/aid/'
        self.tt = mommy.make(TicketType, date_from=now, date_to=now + day, attendee_type=TicketType.AID)

    def test_post_valid_data_saves_object_and_returns_uuid(self):
        data = {
            'type_uuid': self.tt.uuid,
            'title': Speaker.TITLE_MR,
            'first_name': 'Richard',
            'last_name': 'Kellner',
            'email': 'richard@example.com',
            'description': 'I need this ticket'
        }
        response = self.client.post(self.url, data, format='json')

        tickets = Ticket.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'key': tickets.first().uuid})
        self.assertEqual(tickets.count(), 1)

    def test_invalid_data_shows_validation_erros(self):
        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            'type_uuid': ['This field is required.'],
            'first_name': ['This field is required.'],
            'last_name': ['This field is required.'],
            'email': ['This field is required.'],
            'description': ['This field is required.'],
        })

    def test_get_ticket_by_uuid(self):
        ticket = mommy.make(Ticket, type=self.tt)
        response = self.client.get(self.url + str(ticket.uuid) + '/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(response.content.decode('utf-8')), {
            'type_uuid': str(ticket.type_uuid()),
            'title': ticket.title,
            'first_name': ticket.first_name,
            'last_name': ticket.last_name,
            'email': ticket.email,
            'phone': ticket.phone,
            'description': ticket.description
        })

    def test_update_ticket(self):
        ticket = Ticket.objects.create(
            type=self.tt,
            status=Ticket.REQUESTED,
            title=Speaker.TITLE_MR,
            first_name='Richard',
            last_name='Kellner',
            email='richard@example.com',
            description='Old description',
        )

        type_uuid = ticket.type_uuid()
        attendee_tt = mommy.make(TicketType, date_from=now, date_to=now + day, attendee_type=TicketType.ATTENDEE)

        data = {
            'type_uuid': attendee_tt.uuid,  # Ticket switch for non AID is not allowed
            'status': Ticket.REGISTERED,  # Status change should be ignored
            'title': '',
            'first_name': 'Zoltan',
            'last_name': 'Onody',
            'email': 'zoli@example.com',
            'phone': '000000000',
            'description': 'New description'
        }

        response = self.client.put(self.url + str(ticket.uuid) + '/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            'type_uuid': ['Aid ticket type with uuid {} not found.'.format(attendee_tt.uuid)],
        })

        data['type_uuid'] = type_uuid  # Return original AID ticket type and test update

        response = self.client.put(self.url + str(ticket.uuid) + '/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ticket = Ticket.objects.first()
        self.assertEqual(Ticket.objects.count(), 1)
        self.assertEqual(ticket.type_uuid(), type_uuid)
        self.assertEqual(ticket.status, Ticket.REQUESTED)
        self.assertEqual(ticket.title, '')
        self.assertEqual(ticket.first_name, 'Zoltan')
        self.assertEqual(ticket.last_name, 'Onody')
        self.assertEqual(ticket.email, 'zoli@example.com')
        self.assertEqual(ticket.phone, '000000000')
        self.assertEqual(ticket.description, 'New description')


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

    def test_get_cfp_by_uuid(self):
        talk = mommy.make(Talk, event=self.event)
        response = self.client.get('/talks/' + str(talk.uuid) + '/', format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(json.loads(response.content.decode('utf-8')), {
            'event_uuid': str(talk.event_uuid()),
            'title': talk.title,
            'abstract': talk.abstract,
            'type': talk.type,
            'duration': talk.duration,
            'language': talk.language,
            'flag': talk.flag,
            'primary_speaker': {
                'bio': talk.primary_speaker.bio,
                'country': talk.primary_speaker.country,
                'email': talk.primary_speaker.email,
                'first_name': talk.primary_speaker.first_name,
                'last_name': talk.primary_speaker.last_name,
                'phone': talk.primary_speaker.phone,
                'social_url': talk.primary_speaker.social_url,
                'title': talk.primary_speaker.title,
                'url': talk.primary_speaker.url,
            }
        })

    def test_update_cfp(self):
        talk = Talk.objects.create(
            event=self.event,
            title='Old title',
            abstract='Old abstract',
            status=Talk.CFP,
            duration=45,
            primary_speaker=Speaker.objects.create(
                first_name='Zoli',
                last_name='Typo',
                email='zoli@exampl.ecom'
            ),
            secondary_speaker=Speaker.objects.create(
                first_name='Riso',
                last_name='Typo',
                email='riso@exampl.ecom',
            )
        )

        event_uuid = talk.event_uuid()

        data = {
            'event_uuid': event_uuid,
            'title': 'New title',
            'abstract': 'New abstract',
            'duration': 30,
            'status': Talk.APPROVED,  # This cannot be changed!
            'primary_speaker': {
                'first_name': 'Zoltan',
                'last_name': 'Onody',
                'email': 'zoli@example.com',
            },
            'secondary_speaker': {
                'first_name': 'Richard',
                'last_name': 'Kellner',
                'email': 'riso@example.com',
            }
        }

        response = self.client.put('/talks/' + str(talk.uuid) + '/', data, format='json')

        self.maxDiff = None
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        talk = Talk.objects.first()

        self.assertEqual(Talk.objects.count(), 1)
        self.assertEqual(talk.event_uuid(), event_uuid)
        self.assertEqual(talk.status, Talk.CFP)
        self.assertEqual(talk.title, 'New title')
        self.assertEqual(talk.abstract, 'New abstract')
        self.assertEqual(talk.duration, 30)
        self.assertEqual(talk.primary_speaker.first_name, 'Zoltan')
        self.assertEqual(talk.primary_speaker.last_name, 'Onody')
        self.assertEqual(talk.primary_speaker.email, 'zoli@example.com')
        self.assertEqual(talk.secondary_speaker.first_name, 'Richard')
        self.assertEqual(talk.secondary_speaker.last_name, 'Kellner')
        self.assertEqual(talk.secondary_speaker.email, 'riso@example.com')
