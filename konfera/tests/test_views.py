from django.test import TestCase

from konfera.models import Event, Location


class TestEventList(TestCase):
    def setUp(self):
        self.location = Location.objects.create(
            title='FIIT', street='Ilkovicova', city='Bratislava', postcode='841 04', state='Slovakia', capacity=400,
        )
        self.one = Event.objects.create(
            title='One', slug='one', description='First one', event_type='conference', status='published',
            location=self.location, date_from='2015-01-01 01:01:01+01:00', date_to='2015-01-03 01:01:01+01:00',
        )

    def test_redirect_one_event(self):
        response = self.client.get('/event/')
        self.assertRedirects(response, '/event/one/details/')

    def test_event_list(self):
        two = Event.objects.create(
            title='Two', slug='two', description='Second one', event_type='conference', status='published',
            location=self.location, date_from='2016-01-01 01:01:01+01:00', date_to='2016-01-03 01:01:01+01:00',
        )

        response = self.client.get('/event/')

        self.assertTemplateUsed(response, 'konfera/events.html')
        self.assertEquals(list(response.context['events']), [self.one, two])
