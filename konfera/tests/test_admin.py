from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from konfera.admin import EventAdmin, OrderAdmin
from konfera.models import Event, Order


class MockRequest(object):
    pass


class MockSuperUser(object):
    def has_perm(self, perm):
        return True


request = MockRequest()
request.user = MockSuperUser()


class ModelAdminTests(TestCase):
    fixtures = ['test_data.json']

    def setUp(self):
        self.site = AdminSite()

    def test_default_fields(self):
        ev = EventAdmin(Event, self.site)
        event = Event.objects.get(title='PyCon SK 2016')
        ev_default_fields = ['date_from', 'date_to', 'title', 'slug', 'description', 'event_type', 'status',
                             'location', 'sponsors', 'footer_text', 'analytics', 'cfp_allowed', 'cfp_end',
                             'contact_email', 'coc', 'coc_phone', 'coc_phone2', 'uuid', 'date_created',
                             'date_modified']

        self.assertEqual(list(ev.get_fields(request)), ev_default_fields)
        self.assertEqual(list(ev.get_fields(request, event)), ev_default_fields)

        ordr = OrderAdmin(Order, self.site)
        # order = Event.objects.get(uuid='PyCon SK 2016')
        ordr_default_fields = ['status', 'purchase_date', 'payment_date', 'amount_paid', 'uuid',
                               'date_created', 'date_modified', 'variable_symbol', 'price', 'discount']

        self.assertEqual(list(ordr.get_fields(request)), ordr_default_fields)
        # self.assertEqual(list(ordr.get_fields(request, order)), ordr_default_fields)

    def test_default_fieldsets(self):
        ev = EventAdmin(Event, self.site)
        event = Event.objects.get(title='PyCon SK 2016')
        ev_default_fieldsets = (
            (_('Description'), {
                'fields': ('title', 'slug', 'description'),
            }),
            (_('Dates'), {
                'fields': ('date_from', 'date_to', 'cfp_end'),
            }),
            (_('Details'), {
                'fields': ('uuid', 'event_type', 'status', 'location', 'footer_text', 'analytics'),
            }),
            (_('Modifications'), {
                'fields': ('date_created', 'date_modified'),
                'classes': ('collapse',),
            }),
        )

        self.assertEqual(ev.get_fieldsets(request), ev_default_fieldsets)
        self.assertEqual(ev.get_fieldsets(request, event), ev_default_fieldsets)

        order = OrderAdmin(Event, self.site)
        order_default_fieldsets = (
            (_('Details'), {
                'fields': ('uuid', 'variable_symbol', 'price', 'discount', 'status', 'amount_paid'),
            }),
            (_('Modifications'), {
                'fields': ('purchase_date', 'payment_date', 'date_created', 'date_modified'),
                'classes': ('collapse',),
            }),
        )

        self.assertEqual(order.get_fieldsets(request), order_default_fieldsets)
        # self.assertEqual(order.get_fieldsets(request, self.order), order_default_fieldsets)
