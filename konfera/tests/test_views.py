import os
from datetime import timedelta

from django import VERSION
from django.conf import settings
from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from konfera.models import EmailTemplate, Event, Location, Organizer, Speaker, Sponsor, Talk, TicketType, Ticket
from konfera.models.order import Order
from konfera import settings as konfera_settings
from .utils import custom_override_settings

if VERSION[1] in (8, 9):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

now = timezone.now()
day = timedelta(days=1)
hour = timedelta(hours=1)

past = now - 365 * day
future = now + 365 * day


class TestEventRedirect(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', country='SK', capacity=400,
        )
        self.one = Event.objects.create(
            title='One', slug='one', description='First one', event_type=Event.CONFERENCE, status=Event.PUBLISHED,
            location=self.location, date_from=past, date_to=past + day, cfp_allowed=False
        )

    def test_redirects(self):
        response = self.client.get('/events/')
        self.assertEquals(len(Event.objects.published()), 1)
        self.assertRedirects(response, '/one/')

        two = Event.objects.create(
            title='Two', slug='two', description='Second one', event_type=Event.CONFERENCE, status=Event.PUBLISHED,
            location=self.location, date_from=past + 7 * day, date_to=past + 9 * day, cfp_allowed=False
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
            location=self.location, date_from=past, date_to=past + 2 * day, cfp_end=past - day,
        )
        self.event_not_allowed_cfp = Event.objects.create(
            title='CFP not allowed at this event', slug='cfp-not-allowed', description='CFP not allowed',
            event_type='conference', status='published', cfp_allowed=False,
            location=self.location, date_from=past, date_to=past + 2 * day
        )
        self.event_after_cfp_deadline = Event.objects.create(
            title='Passed CFP deadline', slug='passed-cfp', description='Passed deadline',
            event_type='conference', status='published', cfp_end=now - hour,
            location=self.location, date_from=now + hour, date_to=now + 2 * day
        )

    def _get_existing_event(self):
        url = reverse('event_cfp_form', kwargs={'slug': 'one'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        return url, response

    @staticmethod
    def _speaker_form_minimal_data():
        data = {
            'speaker-first_name': 'Tester',
            'speaker-last_name': 'Testovac',
            'speaker-email': 'test@example.com',
            'speaker-bio': 'Something about speaker Tester Testovac',
            'speaker-country': 'SK',
        }

        # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
        APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        avatar = os.path.join(APP_DIR, 'static', 'konfera', 'images', 'no_avatar.png')

        with open(avatar, 'rb') as infile:
            data['speaker-image'] = SimpleUploadedFile('no_avatar.png', infile.read())

        return data

    @staticmethod
    def _talk_form_minimal_data():
        return {
            'talk-title': 'Interesting talk',
            'talk-abstract': 'More text about interesting talk',
            'talk-type': Talk.TALK,
            'talk-duration': 30,
            'talk-language': 'EN',
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

    @custom_override_settings(PROPOSAL_EMAIL_NOTIFY=True)
    def test_cfp_successful_form_submit_notify(self):
        self.assertEquals(settings.PROPOSAL_EMAIL_NOTIFY, True)

        url, response = self._get_existing_event()
        speaker_data = self._speaker_form_minimal_data()
        speaker_data['speaker-email'] = 'notify@example.com'
        talk_data = self._talk_form_minimal_data()
        talk_data['talk-title'] = 'Great talk'
        post_data = dict(speaker_data, **talk_data)
        et = EmailTemplate.objects.get(name='confirm_proposal')
        self.assertEquals(et.counter, 0)

        response = self.client.post(url, post_data)
        et = EmailTemplate.objects.get(name='confirm_proposal')
        self.assertEquals(et.counter, 1)

        # retrieve the talk and speaker from the database
        talk_in_db = Talk.objects.filter(event__slug='one', primary_speaker__email=speaker_data['speaker-email'])
        self.assertEquals(talk_in_db.count(), 1)
        self.assertEquals(talk_in_db[0].title, talk_data['talk-title'])
        self.assertEquals(talk_in_db[0].status, Talk.CFP)

        # Test redirect after submission
        self.assertRedirects(response, reverse('event_details', kwargs={'slug': 'one'}))

    @custom_override_settings(PROPOSAL_EMAIL_NOTIFY=True)
    def test_cfp_successful_form_submit_notify_invalid_email(self):
        url, response = self._get_existing_event()
        speaker_data = self._speaker_form_minimal_data()
        speaker_data['speaker-email'] = 'notify@'
        talk_data = self._talk_form_minimal_data()
        talk_data['talk-title'] = 'Another great talk'
        post_data = dict(speaker_data, **talk_data)

        # post data with invalid email address
        self.client.post(url, data=post_data)

        # counter should not change as email has not been sent
        et = EmailTemplate.objects.get(name='confirm_proposal')
        self.assertEquals(et.counter, 0)


class TestMeetup(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', country='Slovakia', capacity=400,
        )
        Event.objects.create(
            title='Meetup', slug='meetup', description='Fabulous meetup', event_type='meetup', status='published',
            location=self.location, date_from=now - day, date_to=now - 22 * hour, cfp_allowed=False
        )

    def test_get_meetup(self):
        response = self.client.get('/meetup/')
        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # Check if about us text is present
        self.assertIn('Fabulous meetup', str(response.content))


class TestEventOrganizer(TestCase):
    def setUp(self):
        self.location = Location.objects.create(title='FIIT', street='Ilkovicova', city='Bratislava', capacity=400)

    def test_event_organizer(self):
        organizer = Organizer.objects.create(title='Famous Organizer', street='3 Mysterious Lane', city='Far Away',
                                             about_us='We organize things.')
        Event.objects.create(title='Great event', slug='great_event', description='Great event', status='published',
                             event_type='conference', location=self.location, organizer=organizer, cfp_allowed=False,
                             date_from=past, date_to=past + 2 * day)
        response = self.client.get('/great_event/about_us/')

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)
        # Check if about us text is present
        self.assertIn('We organize things.', str(response.content))

    def test_event_no_organizer(self):
        Event.objects.create(title='No Organizer Event', slug='no_org_event', description='No organizer event',
                             status='published', event_type='conference', location=self.location,
                             date_from=past, date_to=past + 2 * day, cfp_allowed=False)
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
            location=self.location, date_from=future, date_to=future + 2 * day, cfp_allowed=False
        )
        self.volunteer = TicketType.objects.create(
            title='Volunteer', description='Volunteer ticket', price=0, attendee_type='volunteer', usage=10,
            accessibility='public', event=self.one, date_from=now - 30 * day, date_to=now + 30 * day
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
            'type': self.volunteer.pk, 'title': 'mr', 'first_name': 'Test', 'last_name': 'Testovac',
            'email': 'test.testovac@example.com', 'description': 'I want to help.',
        })

        # Check that the response is 302 FOUND.
        self.assertEqual(response.status_code, 302)
        ticket = Ticket.objects.get(type_id=self.volunteer.id, email='test.testovac@example.com')

        # Check if redirect to the correct order detail page
        self.assertRedirects(response, reverse(konfera_settings.ORDER_REDIRECT,
                             kwargs={'order_uuid': ticket.order.uuid}))

    @custom_override_settings(REGISTER_EMAIL_NOTIFY=True)
    def test_ticket_register_redirect_notify(self):
        self.assertEquals(settings.REGISTER_EMAIL_NOTIFY, True)

        response = self.client.get('/register/event/one/ticket/volunteer/')
        self.assertEqual(response.status_code, 200)

        et = EmailTemplate.objects.get(name='register_email')
        self.assertEquals(et.counter, 0)

        response = self.client.post('/register/event/one/ticket/volunteer/', {
            'type': self.volunteer.pk, 'title': 'mr', 'first_name': 'Test', 'last_name': 'Notify',
            'email': 'notify@example.com', 'description': 'I want the notification.',
        })
        self.assertEqual(response.status_code, 302)

        ticket = Ticket.objects.get(type_id=self.volunteer.id, email='notify@example.com')
        self.assertRedirects(response, reverse(konfera_settings.ORDER_REDIRECT,
                             kwargs={'order_uuid': ticket.order.uuid}))

        et = EmailTemplate.objects.get(name='register_email')
        self.assertEquals(et.counter, 1)

    def test_register_expired_ticket(self):
        two = Event.objects.create(
            title='Two', slug='two', description='Second one', event_type='conference', status='published',
            location=self.location, date_from=past, date_to=past + 2 * day, cfp_allowed=False
        )
        TicketType.objects.create(
            title='Expired', description='Expired ticket', price=0, attendee_type='volunteer', usage=10, event=two,
            accessibility='public', date_from=past - 99 * day, date_to=past + 49 * day
        )
        response = self.client.get('/register/event/two/ticket/volunteer/')
        self.assertEqual(response.status_code, 302)

        response = self.client.post('/register/event/two/ticket/volunteer/', {
            'title': 'mr', 'first_name': 'Tester', 'last_name': 'Expired', 'email': 'expired@example.com',
            'description': 'Something.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('event_details', kwargs={'slug': two.slug}))

    def test_order_status_cancelled(self):
        response = self.client.get(reverse('order_detail', kwargs={'order_uuid': self.order_cancelled.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['status_label'], 'label-danger')

    def test_order_status_expired(self):
        response = self.client.get(reverse('order_detail', kwargs={'order_uuid': self.order_expired.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['status_label'], 'label-danger')

    def test_order_status_paid(self):
        response = self.client.get(reverse('order_detail', kwargs={'order_uuid': self.order_paid.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['status_label'], 'label-success')

    def test_order_status_await(self):
        response = self.client.get(reverse('order_detail', kwargs={'order_uuid': self.order_await.uuid}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['status_label'], 'label-warning')

    def test_metatags_noindex_nofollow(self):
        response = self.client.get(reverse('order_detail', kwargs={'order_uuid': self.order_paid.uuid}))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")
        self.assertEqual('<meta name="robots" content="noindex,nofollow" />' in content, True)
        self.assertEqual('<meta name="googlebot" content="nosnippet,noarchive" />' in content, True)


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
            status='published', location=self.location, cfp_allowed=False,
            date_from=past, date_to=past + 2 * hour,
        )
        response = self.client.get('')
        # Check if status is OK and correct template is used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'konfera/list_events.html')

    def test_one_conference(self):
        self.old_conference = Event.objects.create(
            title='Old conference', slug='old-conference', description='Old conference', event_type=Event.CONFERENCE,
            status='published', location=self.location, cfp_allowed=False,
            date_from=past, date_to=past + 2 * day,
        )
        response = self.client.get('')
        # Check if the response is 302: redirect to the only existing conference
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/old-conference/')

    def test_latest_conference(self):
        self.new_conference = Event.objects.create(
            title='New conference', slug='new-conference', description='New conference', event_type=Event.CONFERENCE,
            status='published', location=self.location, cfp_allowed=False,
            date_from=future, date_to=future + 2 * day,
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
            location=self.location, date_from=past, date_to=past + 2 * day, cfp_allowed=False
        )
        url = reverse('event_venue', kwargs={'slug': 'one'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_venue_get_here_filled_not_escaped(self):
        Event.objects.create(
            title='Second', slug='second-one', description='Second one', event_type='conference', status='published',
            date_from=past, date_to=past + 2 * day, cfp_allowed=False,
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
            status='published', date_from=past, date_to=past + 2 * day,
            location=location, cfp_allowed=False)
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
            location=location, cfp_allowed=False)
        event.save()
        speaker1 = Speaker.objects.create(first_name='Nice', last_name='Speaker', email='nice@example.com')
        speaker2 = Speaker.objects.create(first_name='Talking', last_name='Speaker', email='talk@example.com')
        speaker3 = Speaker.objects.create(first_name='Spammer', last_name='Speaker', email='talk@example.com')
        speaker4 = Speaker.objects.create(first_name='Assistent', last_name='Speaker', email='nice@example.com')

        Talk.objects.create(
            title='Talk1', abstract='Talk 1', status=Talk.APPROVED, primary_speaker=speaker1, event=event)
        Talk.objects.create(
            title='Talk2', abstract='Talk 2', status=Talk.PUBLISHED, primary_speaker=speaker2, event=event)
        Talk.objects.create(
            title='Talk3', abstract='Talk 3', status=Talk.CFP, primary_speaker=speaker1, event=event)
        Talk.objects.create(
            title='Talk4', abstract='Talk 4', status=Talk.DRAFT, primary_speaker=speaker2, event=event)
        Talk.objects.create(
            title='Talk5', abstract='Talk 5', status=Talk.REJECTED, primary_speaker=speaker3, event=event)
        Talk.objects.create(
            title='Talk6', abstract='Talk 6', status=Talk.WITHDRAWN, primary_speaker=speaker3, event=event)
        Talk.objects.create(
            title='Talk7', abstract='Talk 7', status=Talk.PUBLISHED, primary_speaker=speaker2,
            secondary_speaker=speaker4, event=event)

    def test_speakers_list(self):
        response = self.client.get('/tiny_event/speakers/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'konfera/event/speakers.html')
        self.assertNotIn('Nice Speaker', str(response.content))
        self.assertIn('Talking Speaker', str(response.content))
        self.assertNotIn('Spammer Speaker', str(response.content))
        self.assertIn('Assistent Speaker', str(response.content))


class TestApps(TestCase):
    def test_apps(self):
        from konfera.apps import KonferaConfig
        self.assertEquals(KonferaConfig.name, 'konfera')
