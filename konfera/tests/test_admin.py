import datetime

from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.utils import timezone

from konfera.admin import EventAdmin
from konfera.models import Event, Location


class MockRequest(object):
    pass


class MockSuperUser(object):
    def has_perm(self, perm):
        return True


request = MockRequest()
request.user = MockSuperUser()


class ModelAdminTests(TestCase):

    def setUp(self):
        now = timezone.now()
        location = Location.objects.create(
            title='Test Venue',
            street='Some street',
            city='Bratislava',
            postcode='831 02',
            state='Slovak Republic',
            capacity=400
        )

        self.event = Event.objects.create(
            title='PyCon SK 2017',
            slug='pycon-sk-2017',
            description='Python Conference',
            date_to=now,
            date_from=now + datetime.timedelta(+3),
            event_type='conference',
            status='published',
            location=location
        )
        self.site = AdminSite()

    def test_default_fields(self):
        ev = EventAdmin(Event, self.site)
        default_fields = ['date_from', 'date_to', 'title', 'slug', 'description', 'event_type', 'status', 'location',
                          'sponsors']

        self.assertEqual(list(ev.get_fields(request)), default_fields)
        self.assertEqual(list(ev.get_fields(request, self.event)), default_fields)

    def test_default_fieldsets(self):
        ev = EventAdmin(Event, self.site)
        default_fieldsets = (
            ('Description', {
                'fields': ('title', 'slug', 'description'),
            }),
            ('Dates', {
                'fields': ('date_from', 'date_to'),
            }),
            ('Details', {
                'fields': ('event_type', 'status', 'location'),
            }),
        )

        self.assertEqual(ev.get_fieldsets(request), default_fieldsets)
        self.assertEqual(ev.get_fieldsets(request, self.event), default_fieldsets)
