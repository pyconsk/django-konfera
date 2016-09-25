import datetime

from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from konfera.admin import EventAdmin, OrderAdmin
from konfera.models import Event, Location, Order


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

        self.order = Order.objects.create(
            price=128.0,
            discount=0.5,
        )
        self.site = AdminSite()

    def test_default_fields(self):
        ev = EventAdmin(Event, self.site)
        ev_default_fields = ['date_from', 'date_to', 'title', 'slug', 'description', 'event_type', 'status',
                             'location', 'sponsors']

        self.assertEqual(list(ev.get_fields(request)), ev_default_fields)
        self.assertEqual(list(ev.get_fields(request, self.event)), ev_default_fields)

        order = OrderAdmin(Order, self.site)
        order_default_fields = ['price', 'discount', 'status', 'purchase_date', 'payment_date']

        self.assertEqual(list(order.get_fields(request)), order_default_fields)
        self.assertEqual(list(order.get_fields(request, self.order)), order_default_fields)

    def test_default_fieldsets(self):
        ev = EventAdmin(Event, self.site)
        ev_default_fieldsets = (
            (_('Description'), {
                'fields': ('title', 'slug', 'description'),
            }),
            (_('Dates'), {
                'fields': ('date_from', 'date_to'),
            }),
            (_('Details'), {
                'fields': ('event_type', 'status', 'location'),
            }),
        )

        self.assertEqual(ev.get_fieldsets(request), ev_default_fieldsets)
        self.assertEqual(ev.get_fieldsets(request, self.event), ev_default_fieldsets)

        order = OrderAdmin(Event, self.site)
        order_default_fieldsets = (
            (_('Details'), {
                'fields': ('price', 'discount', 'status'),
            }),
            (_('Dates'), {
                'fields': ('purchase_date', 'payment_date'),
                'classes': ('collapse',),
            }),
        )

        self.assertEqual(order.get_fieldsets(request), order_default_fieldsets)
        self.assertEqual(order.get_fieldsets(request, self.order), order_default_fieldsets)
