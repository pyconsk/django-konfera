from datetime import timedelta
from django import VERSION
from django.contrib import messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import TestCase
from django.utils import timezone
from konfera import models
from django.test.client import RequestFactory

from konfera.models import Event, Location, Organizer, Speaker, Sponsor, Talk, TicketType, Ticket
from konfera.models.order import Order

if VERSION[1] in (8, 9):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse


class TestEventRedirect(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', country='SK', capacity=400,
        )
        self.one = Event.objects.create(
            title='One', slug='one', description='First one', event_type=Event.CONFERENCE, status=Event.PUBLISHED,
            location=self.location, date_from='2015-01-01 01:01:01+01:00', date_to='2015-01-03 01:01:01+01:00',
        )

    def test_redirects(self):
        response = self.client.get('/events/')
        self.assertEquals(len(Event.objects.published()), 1)
        self.assertRedirects(response, '/one/')

        two = Event.objects.create(
            title='Two', slug='two', description='Second one', event_type=Event.CONFERENCE, status=Event.PUBLISHED,
            location=self.location, date_from='2016-01-01 01:01:01+01:00', date_to='2016-01-03 01:01:01+01:00',
        )

        response = self.client.get('/events/')

        self.assertEquals(len(Event.objects.published()), 2)
        self.assertTemplateUsed(response, 'konfera/list_events.html')
        self.assertEquals(list(response.context['event_list']), [two, self.one])


class TestEventList(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', country='Slovakia', capacity=400,
        )
        self.one = Event.objects.create(
            title='One', slug='one', description='First one', event_type='conference', status='published',
            location=self.location, date_from='2015-01-01 01:01:01+01:00', date_to='2015-01-03 01:01:01+01:00',
        )
        self.event_not_allowed_cfp = Event.objects.create(
            title='CFP not allowed at this event', slug='cfp-not-allowed', description='CFP not allowed',
            event_type='conference', status='published', cfp_allowed=False,
            location=self.location, date_from='2015-01-01 01:01:01+01:00', date_to='2015-01-03 01:01:01+01:00'
        )
        self.event_after_cfp_deadline = Event.objects.create(
            title='Passed CFP deadline', slug='passed-cfp', description='Passed deadline',
            event_type='conference', status='published', cfp_end='2015-01-01 01:01:01+01:00',
            location=self.location, date_from='2017-01-01 01:01:01+01:00', date_to='2017-01-03 01:01:01+01:00'
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
            'talk-type': Talk.TALK,
            'talk-duration': 30,
            # 'primary_speaker': 'TBD',
            # 'event': 'TBD',
        }

    def test_cfp_non_existing_event(self):
        url = reverse('event_cfp_form', kwargs={'slug': 'non-existing-event'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_cfp_not_allowed(self):
        url = reverse('event_cfp_form', kwargs={'slug': 'cfp-not-allowed'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_cfp_after_deadline(self):
        url = reverse('event_cfp_form', kwargs={'slug': 'passed-cfp'})
        response = self.client.get(url)
        self.assertIn('Thank you for your interest, but unfortunately call for proposals', str(response.content))

    def test_cfp_existing_event(self):
        url, response = self._get_existing_event()
        self.assertTemplateUsed(response, 'konfera/event/cfp_form.html')

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
        self.assertEquals(talk_in_db[0].status, Talk.CFP)

        # Test redirect after submission
        self.assertRedirects(response, reverse('event_details', kwargs={'slug': 'one'}))


class TestMeetup(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', country='Slovakia', capacity=400,
        )
        Event.objects.create(
            title='Meetup', slug='meetup', description='Fabulous meetup', event_type='meetup', status='published',
            location=self.location, date_from='2016-01-01 17:00:00+01:00', date_to='2016-01-01 19:00:00+01:00',
        )

    def test_get_meetup(self):
        response = self.client.get('/meetup/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # Check if about us text is present
        print(response.content)
        self.assertIn('Fabulous meetup', str(response.content))


class TestEventOrganizer(TestCase):
    def setUp(self):
        self.location = Location.objects.create(title='FIIT', street='Ilkovicova', city='Bratislava', capacity=400)

    def test_event_organizer(self):
        organizer = Organizer.objects.create(title='Famous Organizer', street='3 Mysterious Lane', city='Far Away',
                                             about_us='We organize things.')
        Event.objects.create(title='Great event', slug='great_event', description='Great event', status='published',
                             event_type='conference', location=self.location, organizer=organizer,
                             date_from='2015-01-01 01:01:01+01:00', date_to='2015-01-03 01:01:01+01:00')
        response = self.client.get('/great_event/about_us/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # Check if about us text is present
        self.assertIn('We organize things.', str(response.content))

    def test_event_no_organizer(self):
        Event.objects.create(title='No Organizer Event', slug='no_org_event', description='No organizer event',
                             status='published', event_type='conference', location=self.location,
                             date_from='2015-01-01 01:01:01+01:00', date_to='2015-01-03 01:01:01+01:00')
        response = self.client.get('/no_org_event/about_us/')

        # Check that the response is 404 - organizer not set.
        self.assertEqual(response.status_code, 404)


class TestOrderDetail(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', country='Slovakia', capacity=400,
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
        self.order_cancelled = Order.objects.create(price=200, discount=0, status=Order.CANCELLED)
        self.order_expired = Order.objects.create(price=200, discount=0, status=Order.EXPIRED)
        self.order_paid = Order.objects.create(price=200, discount=0, status=Order.PAID)
        self.order_await = Order.objects.create(price=200, discount=0, status=Order.AWAITING)

    def test_ticket_register_redirect(self):
        response = self.client.get('/register/event/one/ticket/volunteer/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)

        # Register for event as volunteer
        response = self.client.post('/register/event/one/ticket/volunteer/', {
            'title': 'mr', 'first_name': 'Test', 'last_name': 'Testovac', 'email': 'test.testovac@example.com',
            'description': 'I want to help.',
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


class TestIndexRedirect(TestCase):

    def setUp(self):
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', country='Slovakia', capacity=400,
        )

    def test_no_conference(self):
        response = self.client.get('')
        # Check if status is OK and correct template is used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'konfera/list_events.html')
        # test correct alert class
        self.assertIn('alert alert-info', str(response.content))

        self.old_meetup = Event.objects.create(
            title='Old meetup', slug='old-meetup', description='Old meetup', event_type=Event.MEETUP,
            status='published', location=self.location,
            date_from='2016-01-01 01:01:01+01:00', date_to='2016-01-01 01:01:01+01:00',
        )
        response = self.client.get('')
        # Check if status is OK and correct template is used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'konfera/list_events.html')

    def test_one_conference(self):
        self.old_conference = Event.objects.create(
            title='Old conference', slug='old-conference', description='Old conference', event_type=Event.CONFERENCE,
            status='published', location=self.location,
            date_from='2016-01-01 01:01:01+01:00', date_to='2016-01-03 01:01:01+01:00',
        )
        response = self.client.get('')
        # Check if the response is 302: redirect to the only existing conference
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/old-conference/')

    def test_latest_conference(self):
        self.new_conference = Event.objects.create(
            title='New conference', slug='new-conference', description='New conference', event_type=Event.CONFERENCE,
            status='published', location=self.location,
            date_from='2017-01-01 01:01:01+01:00', date_to='2017-01-03 01:01:01+01:00',
        )
        response = self.client.get('')
        # Check if the response is 302: redirect to the latest conference (default LANDING_PAGE = latest_conference)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/new-conference/')


class TestEventVenue(TestCase):
    def setUp(self):
        self.html_code = '<strong>test</strong>'
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', country='SK', capacity=400,
        )
        self.location_with_venue = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', country='SK', capacity=400,
            get_here=self.html_code,
        )

    def test_venue_non_existing_event(self):
        url = reverse('event_venue', kwargs={'slug': 'non-existing-event'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_venue_get_here_not_filled(self):
        Event.objects.create(
            title='One', slug='one', description='First one', event_type='conference', status='published',
            location=self.location, date_from='2015-01-01 01:01:01+01:00', date_to='2015-01-03 01:01:01+01:00',
        )
        url = reverse('event_venue', kwargs={'slug': 'one'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_venue_get_here_filled_not_escaped(self):
        Event.objects.create(
            title='Second', slug='second-one', description='Second one', event_type='conference', status='published',
            date_from='2015-01-01 01:01:01+01:00', date_to='2015-01-03 01:01:01+01:00',
            location=self.location_with_venue,
        )
        url = reverse('event_venue', kwargs={'slug': 'second-one'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'konfera/event/venue.html')
        self.assertTrue(self.html_code in response.content.decode('utf-8'))


class TestSponsorsListView(TestCase):
    def setUp(self):
        location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', country='SK', capacity=400,)
        sponsor1 = Sponsor.objects.create(title='Sponsor 1', type=1, about_us='Platinum Sponsor')
        sponsor2 = Sponsor.objects.create(title='Sponsor 2', type=2, about_us='Gold Sponsor')
        evt = Event.objects.create(
            title='Small Event', slug='small_event', description='Small event', event_type='conference',
            status='published', date_from='2015-01-01 01:01:01+01:00', date_to='2015-01-03 01:01:01+01:00',
            location=location,)
        evt.sponsors.add(sponsor1)
        evt.sponsors.add(sponsor2)

    def test_sponsors_list(self):
        response = self.client.get('/small_event/sponsors/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'konfera/event/sponsors.html')
        self.assertIn('Sponsor 1', str(response.content))
        self.assertIn('Sponsor 2', str(response.content))


class TestSpeakersListView(TestCase):
    def setUp(self):
        location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', country='SK', capacity=400,)
        event = Event.objects.create(
            title='Tiny Event', slug='tiny_event', description='Tiny event', event_type='conference',
            status='published', date_from='2016-01-01 01:01:01+01:00', date_to='2016-01-03 01:01:01+01:00',
            location=location,)
        event.save()
        speaker1 = Speaker.objects.create(first_name='Nice', last_name='Speaker', email='nice@example.com')
        speaker2 = Speaker.objects.create(first_name='Talking', last_name='Speaker', email='talk@example.com')
        Talk.objects.create(
            title='Talk1', abstract='Talk 1', status=Talk.APPROVED, primary_speaker=speaker1, event=event)
        Talk.objects.create(
            title='Talk2', abstract='Talk 2', status=Talk.APPROVED, primary_speaker=speaker2, event=event)

    def test_speakers_list(self):
        response = self.client.get('/tiny_event/speakers/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'konfera/event/speakers.html')
        self.assertIn('Nice Speaker', str(response.content))
        self.assertIn('Talking Speaker', str(response.content))
