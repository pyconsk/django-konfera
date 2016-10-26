from django import VERSION
from django.test import TestCase

from konfera.models import Event, Location, Talk, TicketType, Ticket
from konfera.models.order import Order, CANCELLED, EXPIRED, PAID, AWAITING
from konfera.models.talk import CFP, TALK
from konfera.models.event import PUBLISHED, CONFERENCE

if VERSION[1] in (8, 9):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse


class TestEventRedirect(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', state='Slovakia', capacity=400,
        )
        self.one = Event.objects.create(
            title='One', slug='one', description='First one', event_type=CONFERENCE, status=PUBLISHED,
            location=self.location, date_from='2015-01-01 01:01:01+01:00', date_to='2015-01-03 01:01:01+01:00',
        )

    def test_redirects(self):
        response = self.client.get('/events/')
        self.assertEquals(len(Event.objects.published()), 1)
        self.assertRedirects(response, '/one/')

        two = Event.objects.create(
            title='Two', slug='two', description='Second one', event_type=CONFERENCE, status=PUBLISHED,
            location=self.location, date_from='2016-01-01 01:01:01+01:00', date_to='2016-01-03 01:01:01+01:00',
        )

        response = self.client.get('/events/')

        self.assertEquals(len(Event.objects.published()), 2)
        self.assertTemplateUsed(response, 'konfera/list_events.html')
        self.assertEquals(list(response.context['event_list']), [two, self.one])


class TestEventList(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', state='Slovakia', capacity=400,
        )
        self.one = Event.objects.create(
            title='One', slug='one', description='First one', event_type='conference', status='published',
            location=self.location, date_from='2015-01-01 01:01:01+01:00', date_to='2015-01-03 01:01:01+01:00',
        )

    def _get_existing_event(self):
        url = reverse('event_cfp_form', kwargs={'slug': 'one'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        return url, response

    @staticmethod
    def _speaker_form_minimal_data():
        return {
            'speaker-first_name': 'Tester',
            'speaker-last_name': 'Testovac',
            'speaker-title': 'none',
            'speaker-email': 'test@example.com',
            'speaker-bio': 'Something about speaker Tester Testovac',
            'speaker-country': 'SK',
        }

    @staticmethod
    def _talk_form_minimal_data():
        return {
            'talk-title': 'Interesting talk',
            'talk-abstract': 'More text about interesting talk',
            'talk-type': TALK,
            'talk-duration': 30,
            # 'primary_speaker': 'TBD',
            # 'event': 'TBD',
        }

    def test_cfp_non_existing_event(self):
        url = reverse('event_cfp_form', kwargs={'slug': 'non-existing-event'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_cfp_existing_event(self):
        url, response = self._get_existing_event()
        self.assertTemplateUsed(response, 'konfera/cfp_form.html')

    def test_cfp_successful_form_submit(self):
        url, response = self._get_existing_event()
        speaker_data = self._speaker_form_minimal_data()
        talk_data = self._talk_form_minimal_data()
        post_data = dict(speaker_data, **talk_data)

        response = self.client.post(url, data=post_data)

        # retrieve the talk and speaker from the database
        talk_in_db = Talk.objects.filter(event__slug='one', primary_speaker__email=speaker_data['speaker-email'])
        self.assertEquals(talk_in_db.count(), 1)
        self.assertEquals(talk_in_db[0].title, talk_data['talk-title'])
        self.assertEquals(talk_in_db[0].status, CFP)

        # Test redirect after submission
        self.assertRedirects(response, reverse('event_details', kwargs={'slug': 'one'}))


class TestOrderDetail(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', state='Slovakia', capacity=400,
        )
        self.one = Event.objects.create(
            title='One', slug='one', description='First one', event_type='conference', status='published',
            location=self.location, date_from='2017-01-01 01:01:01+01:00', date_to='2017-01-03 01:01:01+01:00',
        )
        self.volunteer = TicketType.objects.create(
            title='Volunteer', description='Volunteer ticket', price=0, attendee_type='volunteer', usage=10,
            accessibility='public', event=self.one, date_from='2016-07-01 01:01:01+01:00',
            date_to='2016-12-01 01:01:01+01:00'
        )
        self.order_cancelled = Order.objects.create(price=200, discount=0, status=CANCELLED)
        self.order_expired = Order.objects.create(price=200, discount=0, status=EXPIRED)
        self.order_paid = Order.objects.create(price=200, discount=0, status=PAID)
        self.order_await = Order.objects.create(price=200, discount=0, status=AWAITING)

    def test_ticket_register_redirect(self):
        response = self.client.get('/register/event/one/ticket/volunteer/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Register for event as volunteer
        response = self.client.post('/register/event/one/ticket/volunteer/', {
            'title': 'mr', 'first_name': 'Test', 'last_name': 'Testovac', 'email': 'test.testovac@example.com'
        })

        # Check that the response is 302 FOUND.
        self.assertEqual(response.status_code, 302)
        ticket = Ticket.objects.get(type_id=self.volunteer.id, email='test.testovac@example.com')

        # Check if redirect to the correct order detail page
        self.assertRedirects(response, reverse('order_details', kwargs={'order_uuid': ticket.order.uuid}))

    def test_order_status_cancelled(self):
        response = self.client.get(reverse('order_details', kwargs={'order_uuid': self.order_cancelled.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['status_label'], 'label-danger')

    def test_order_status_expired(self):
        response = self.client.get(reverse('order_details', kwargs={'order_uuid': self.order_expired.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['status_label'], 'label-danger')

    def test_order_status_paid(self):
        response = self.client.get(reverse('order_details', kwargs={'order_uuid': self.order_paid.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['status_label'], 'label-success')

    def test_order_status_await(self):
        response = self.client.get(reverse('order_details', kwargs={'order_uuid': self.order_await.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['status_label'], 'label-warning')
