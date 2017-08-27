from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from model_mommy import mommy

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
    def setUp(self):
        self.site = AdminSite()
        self.event = mommy.make(Event, title='PyCon SK 2016')

    def test_default_fields(self):
        ev = EventAdmin(Event, self.site)
        event = Event.objects.get(title='PyCon SK 2016')
        ev_default_fields = ['date_from', 'date_to', 'title', 'slug', 'status', 'organizer', 'cfp_end', 'uuid',
                             'date_created', 'date_modified']

        self.assertEqual(list(ev.get_fields(request)), ev_default_fields)
        self.assertEqual(list(ev.get_fields(request, event)), ev_default_fields)

        ordr = OrderAdmin(Order, self.site)
        # order = Event.objects.get(uuid='PyCon SK 2016')
        ordr_default_fields = [
            'amount_paid', 'processing_fee', 'status', 'payment_date', 'unpaid_notification_sent_amount',
            'purchase_date', 'uuid', 'date_created', 'date_modified', 'variable_symbol', 'price', 'discount', 'to_pay',
            'unpaid_notification_sent_at']

        self.assertEqual(list(ordr.get_fields(request)), ordr_default_fields)
        # self.assertEqual(list(ordr.get_fields(request, order)), ordr_default_fields)

    def test_default_fieldsets(self):
        ev = EventAdmin(Event, self.site)
        event = Event.objects.get(title='PyCon SK 2016')
        ev_default_fieldsets = (
            ('Description', {
                'fields': ('title', 'slug', 'organizer'),
            }),
            ('Dates', {
                'fields': ('date_from', 'date_to', 'cfp_end')
            }),
            ('Details', {
                'fields': ('uuid', 'status')
            }),
            ('Modifications', {
                'fields': ('date_created', 'date_modified'), 'classes': ('collapse',)
            })
        )

        self.assertEqual(ev.get_fieldsets(request), ev_default_fieldsets)
        self.assertEqual(ev.get_fieldsets(request, event), ev_default_fieldsets)

        order = OrderAdmin(Event, self.site)
        order_default_fieldsets = (
            ('Details', {
                'fields': ( 'uuid', 'variable_symbol', 'price', 'discount', 'processing_fee', 'to_pay', 'status',
                            'amount_paid', 'unpaid_notification_sent_at')
            }),
            ('Modifications', {
                'fields': ('purchase_date', 'payment_date', 'date_created', 'date_modified'), 'classes': ('collapse',)
            })
        )

        self.assertEqual(order.get_fieldsets(request), order_default_fieldsets)
        self.assertEqual(order.get_fieldsets(request, order), order_default_fieldsets)
