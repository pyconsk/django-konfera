import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.utils.text import slugify
from model_mommy import mommy

from konfera import models
from konfera.models.discount_code import DiscountCode
from konfera.models.event import Event
from konfera.models.order import Order
from konfera.models.organizer import Organizer
from konfera.models.speaker import Speaker
from konfera.models.talk import Talk
from konfera.models.ticket import Ticket
from konfera.models.ticket_type import TicketType


now = timezone.now()
hour = datetime.timedelta(hours=1)
day = datetime.timedelta(days=1)
earlier = now - 8 * hour
later = now + 8 * hour
past = now - 3 * day
future = now + 3 * day
distant_past = now - 3650 * day
distant_future = now + 3650 * day


class EventTest(TestCase):

    def setUp(self):
        self.event = mommy.make(Event)

    def test_string_representation(self):
        """
        Test string representation of the Event object.
        """
        self.assertEquals(str(self.event), self.event.title)

    def test_dates(self):
        """
        Test Event dates, that it cant end before it has started, and either none or both start/end has to be defined.
        """
        self.event.date_from = None
        self.event.date_to = now
        self.assertRaises(ValidationError, self.event.clean)

        self.event.date_from = now
        self.event.date_to = None
        self.assertRaises(ValidationError, self.event.clean)

        self.event.date_to = now
        self.event.date_from = now + 3 * day
        self.assertRaises(ValidationError, self.event.clean)

        self.event.date_from = now
        self.event.date_to = now + day
        self.assertIsNone(self.event.clean())

        self.event.date_from = None
        self.event.date_to = None
        self.assertIsNone(self.event.clean())

    def test_cfp(self):
        """
        Test Event CfP, if it is set or not and different time traveling scenarios.
        """
        self.event.date_from = now
        self.event.date_to = self.event.date_from + 2 * day
        self.event.cfp_end = self.event.date_to + day  # CfP ends 1 day after event
        self.assertEquals(False, self.event.cfp_open)
        self.assertRaises(ValidationError, self.event.clean)

        self.event.date_from = now + 365 * day
        self.event.date_to = self.event.date_from + 2 * day
        self.event.cfp_end = self.event.date_from - day  # CfP ends 1 day before event
        self.assertEquals(True, self.event.cfp_open)
        self.assertIsNone(self.event.clean())

        self.event.date_from = now + 7 * day
        self.event.date_to = self.event.date_from + 2 * day
        self.event.cfp_end = self.event.date_from  # CfP ends at event starts
        self.assertIsNone(self.event.clean())
        self.assertEquals(True, self.event.cfp_open)

        self.event.date_from = now + 7 * day
        self.event.date_to = self.event.date_from + 2 * day
        self.event.cfp_end = self.event.date_to  # CfP ends at event ends (we allow it)
        self.assertIsNone(self.event.clean())
        self.assertEquals(True, self.event.cfp_open)

        self.event.cfp_end = None
        self.assertEquals(False, self.event.cfp_open)  # CfP not set
        self.assertIsNone(self.event.clean())

    def test_slug(self):
        """
        Test event slug, that it is unique.
        """
        title_length = Event._meta.get_field('title').max_length
        slug_length = Event._meta.get_field('slug').max_length
        self.assertGreaterEqual(slug_length, title_length)

        event = mommy.make(Event)
        slug = slugify(event.title)
        event.slug = slug
        event.save()
        self.assertEqual(Event.objects.get(slug=slug).title, event.title)  # In certain cases (underscores) might fail!

        event2 = mommy.make(Event)
        event2.slug = slug
        self.assertRaises(IntegrityError, event2.save)  # slug must be unique


class SpeakerTest(TestCase):

    def setUp(self):
        self.speaker = mommy.make(Speaker)

    def test_string_representation(self):
        """
        Test string representation of the Speaker object.
        """
        self.assertEquals(str(self.speaker), '%s %s' % (self.speaker.first_name, self.speaker.last_name))
        self.speaker.title = 'mr'
        self.assertEquals(str(self.speaker), '%s %s' % (self.speaker.first_name, self.speaker.last_name))


class TalkTest(TestCase):

    def setUp(self):
        self.talk = mommy.make(Talk)

    def test_string_representation(self):
        """
        Test string representation of the Talk object.
        """
        self.assertEquals(str(self.talk), self.talk.title)

    def test_different_speakers(self):
        """
        Test that one speaker can not be primary and secondary as well.
        """
        speaker1 = mommy.make(Speaker)
        speaker2 = mommy.make(Speaker)
        talk = mommy.make(Talk)

        talk.primary_speaker = speaker1
        self.assertTrue(talk.clean)
        talk.secondary_speaker = speaker2
        self.assertTrue(talk.clean)
        talk.secondary_speaker = speaker1
        self.assertRaises(ValidationError, talk.clean)


class TicketTypeTest(TestCase):

    def setUp(self):
        # this creates related Event in the DB.
        self.tt = mommy.make(TicketType, date_from=now - 7 * day, date_to=now - 5 * day)

    def test_string_representation(self):
        """
        Test string representation of the TicketType object.
        """
        self.assertEquals(str(self.tt), self.tt.title)

    def test_clean_dates(self):
        """
        Cleaning models dates follow different type of rules, also depending on event.
        """
        self.tt.date_from = now - 7 * day
        self.tt.date_to = now - 5 * day
        self.tt.event.date_from = now - 30 * day
        self.tt.event.date_to = now - 25 * day
        # Ended in the past and ticket type dates after event
        self.assertRaises(ValidationError, self.tt.clean)

        self.tt.date_from = None
        self.tt.date_to = None
        # Ended event and no dates raises error
        self.assertRaises(ValidationError, self.tt.clean)

        # End date can not be before start date
        self.tt.date_from = now - 27 * day
        self.tt.date_to = now - 30 * day
        self.assertRaises(ValidationError, self.tt.clean)

        # Correct data in the past before event, SAVE.
        self.tt.date_from = now - 40 * day
        self.tt.clean()
        self.tt.save()

        future_tt = mommy.make(TicketType, date_from=now + 7 * day, date_to=now + 10 * day)
        future_tt.date_from = None
        future_tt.date_to = None
        future_tt.event.date_from = now + 150 * day
        future_tt.event.date_to = now + 160 * day
        future_tt.event.save()
        # Future event pre-populate the dates
        future_tt.clean()

        self.assertEquals(future_tt.date_from > now, True)
        self.assertEquals(future_tt.date_to, future_tt.event.date_to)

    def test_status(self):
        """
        Test the status of TicketType in different dates scenarios.
        """
        self.tt.date_from = None
        self.tt.date_to = None
        self.tt.event.date_from = now + 25 * day
        self.tt.event.date_to = now + 30 * day

        # Dates are not set or are in future ticket type is not available
        self.assertEquals(self.tt.status, TicketType.STATUSES[TicketType.NOT_AVAILABLE])
        self.tt.date_from = now + day
        self.assertEquals(self.tt.status, TicketType.STATUSES[TicketType.NOT_AVAILABLE])
        self.tt.date_to = now + 3 * day
        self.assertEquals(self.tt.status, TicketType.STATUSES[TicketType.NOT_AVAILABLE])

        # ticket type is within the date range so it is TicketType.active
        self.tt.date_from = now - day
        self.assertEquals(self.tt.status, TicketType.STATUSES[TicketType.ACTIVE])

        self.tt.usage = 0
        self.assertEquals(self.tt.status, TicketType.STATUSES[TicketType.SOLDOUT])

        # passed ticket types we consider as TicketType.expired
        self.tt.date_from = now - 3 * day
        self.tt.date_to = now - day
        self.assertEquals(self.tt.status, TicketType.STATUSES[TicketType.EXPIRED])


class DiscountCodeTest(TestCase):

    def setUp(self):
        self.tt = mommy.make(TicketType, date_from=now - 7 * day, date_to=now - 5 * day)
        self.dc = mommy.make(DiscountCode, date_from=now - 7 * day, date_to=now - 5 * day, ticket_type=self.tt)

    def test_string_representation(self):
        """
        Test string representation of the DiscountCode object.
        """
        self.assertEqual(str(self.dc), self.dc.title)

    def test_clean_dates(self):
        """
        Cleaning models dates follow different type of rules, also depending on event.
        """
        self.dc.date_from = None
        self.dc.date_to = None

        # Clean will prepopulate dates from ticket type
        self.dc.clean()
        self.assertEquals(self.dc.date_from, self.dc.ticket_type.date_from)
        self.assertEquals(self.dc.date_to, self.dc.ticket_type.date_to)

        # Discount can not be outside ticket type date range
        self.dc.date_from = self.dc.ticket_type.date_from - hour
        self.assertRaises(ValidationError, self.dc.clean)
        self.dc.date_from = self.dc.ticket_type.date_from
        self.dc.date_to = self.dc.ticket_type.date_to + hour
        self.assertRaises(ValidationError, self.dc.clean)

    def test_discount_values(self):
        """
        Discount is in percentage.
        """
        self.dc.discount = 0
        self.dc.full_clean()
        self.dc.discount = 100
        self.dc.full_clean()
        self.dc.discount = -1
        self.assertRaises(ValidationError, self.dc.full_clean)
        self.dc.discount = 101
        self.assertRaises(ValidationError, self.dc.full_clean)


class OrderTest(TestCase):

    def setUp(self):
        self.order = mommy.make(Order)

    def test_string_representation(self):
        """
        Test string representation of the Order object.
        """
        self.assertEquals(str(self.order), str(self.order.price - self.order.discount))
        self.order.price = 155.5
        self.order.discount = 5.5
        self.assertEquals(str(self.order), str(self.order.price - self.order.discount))

    def test_unpaid_order_save(self):
        """
        Test Unpaid Order behaviour when saving. Status have to be AWAITING and payment_date not set.
        """
        order = mommy.make(Order)
        order.save()
        self.assertIsNone(order.payment_date)
        self.assertEqual(order.status, Order.AWAITING)

    def test_paid_order_save(self):
        """
        Test payment_date generation once the order status is changed to PAID.
        """
        order = mommy.make(Order)
        order.status = Order.PAID
        order.save()
        self.assertIsNotNone(order.payment_date)

    def test_to_pay(self):
        """
        Test calculation how much should be paid.

        TODO: Test negative numbers and also decimals.
        """
        self.order.price = 155.5
        self.order.discount = 5.5
        self.assertEqual(self.order.to_pay, 150)
        self.order.processing_fee = 50
        self.assertEqual(self.order.to_pay, 200)

    def test_left_to_pay(self):
        """
        Test scenarion where amount pais is less or more than it should be.
        """
        self.order.price = 155.5
        self.order.discount = 5.5
        self.order.processing_fee = 50
        self.order.amount_paid = 100
        self.assertEqual(self.order.left_to_pay, 100)  # paid less
        self.order.amount_paid = 500
        self.assertEqual(self.order.left_to_pay, 0)  # paid more

    def test_order_event_with_ticket(self):
        """
        Test to find related events.

        Create Ticket Type for event and add Tickets to Order and check if Event is found. Oder and Event has no direct
        relation.
        """
        # TicketType also creates Event as well
        ticket_type = mommy.make(TicketType, date_from=now, date_to=now + 3 * day)

        # Create Ticket with TicketType, order should get event from ticket type
        models.Ticket.objects.create(type=ticket_type, order=self.order)
        self.assertEqual(self.order.event, ticket_type.event)

    def test_order_event_without_ticket(self):
        """
        Test to find related events.

        Empty stored order should not have any related tickets created that belongs to some event.
        """
        order = mommy.make(Order)
        self.assertEqual(order.event, None)


class TicketTest(TestCase):

    def setUp(self):
        self.event = mommy.make(Event, date_from=now + 7 * day, date_to=now + 10 * day)

        self.tt = mommy.make(TicketType, price=100, date_from=now, date_to=self.event.date_from, event=self.event)
        self.tt2 = mommy.make(TicketType, price=10, date_from=now, date_to=self.event.date_from, event=self.event)

        self.dc = mommy.make(DiscountCode, date_from=now, date_to=self.event.date_from, ticket_type=self.tt,
                             discount=60, usage=1)
        self.dc2 = mommy.make(DiscountCode, date_from=now, date_to=self.event.date_from, ticket_type=self.tt2,
                              discount=25, usage=1)

    def test_string_representation(self):
        """
        Test string representation of the Ticket object.
        """
        ticket = mommy.make(Ticket, type=self.tt)
        self.assertEqual(str(ticket), '%s %s' % (ticket.first_name, ticket.last_name))

        ticket.title = 'non-sense'
        self.assertEqual(str(ticket), '%s %s' % (ticket.first_name, ticket.last_name))

        ticket.title = Speaker.TITLE_MR
        self.assertEqual(
            str(ticket),
            '%s %s %s' % (dict(Speaker.TITLE_CHOICES)[ticket.title], ticket.first_name, ticket.last_name)
        )

    def test_automatic_order_generator(self):
        """
        Test order autogeneration and its values. Ticket save generates an order.
        """
        ticket = mommy.make(Ticket, type=self.tt, discount_code=self.dc)
        self.assertEquals(ticket.order.status, Order.AWAITING)
        self.assertEquals(ticket.order.price, ticket.type.price)
        self.assertEquals(ticket.order.discount, ticket.discount_code.discount)

    def test_clean_and_save_ticket_discount_code(self):
        """
        Test DiscountCode use on Ticket, test different mixin and usage scenarios.
        """
        # if saved with no discount_code, the ticket should save successfully
        ticket = mommy.make(Ticket, type=self.tt)
        ticket.discount_code = None
        ticket.save()

        # if saved with a code that matches the ticket type of the ticket, the ticket should save successfully
        mommy.make(Ticket, type=self.tt, discount_code=self.dc)
        # if discount code has been applied, the discount code should not be available
        self.assertIs(self.dc.is_available, False)
        self.assertEquals(self.dc.issued_tickets, 1)

        # if saved with a code that does matches the ticket type of the ticket, but run out of usage should raise an
        # ValidationError
        ticket.discount_code = self.dc
        self.assertRaises(ValidationError, ticket.save)

        # if saved with a code that does not match the ticket type of the ticket, the ticket should
        # raise a validationError
        ticket.discount_code = self.dc2
        # the discount code has not been applied so the number of allowed usages should stay 1
        self.assertRaises(ValidationError, ticket.save)
        self.assertEquals(self.dc2.issued_tickets, 0)

    def test_save_tickets_for_different_event(self):
        """
        Test mixing tickets for different events in one order should result in ValidationError.
        """
        event2 = mommy.make(Event, date_from=now + 360 * day, date_to=now + 365 * day)
        event2_tt = mommy.make(TicketType, price=10, date_from=now, date_to=event2.date_from, event=event2)

        ticket = mommy.make(Ticket, type=self.tt)
        ticket2 = mommy.prepare(Ticket, type=event2_tt, order=ticket.order)

        self.assertRaises(ValidationError, ticket2.save)


class ReceiptTest(TestCase):

    def setUp(self):
        self.order = mommy.make(Order)
        self.receipt = self.order.receipt_of

    def test_string_representation(self):
        """
        Test string representation of the Receipt object.
        """
        self.assertEquals(str(self.receipt), self.receipt.title)
        self.receipt.title = 'Random Name'
        self.assertEquals(str(self.receipt), self.receipt.title)


class OrganizerTest(TestCase):

    def setUp(self):
        self.org = mommy.make(Organizer)

    def test_string_representation(self):
        """
        Test string representation of the Organizer object.
        """
        self.assertEquals(str(self.org), self.org.title)

    def test_required_missing(self):
        """
        Test required fields missing.
        """
        no_title_organizer = Organizer(company_id='999', tax_id='999', vat_id='XX999')
        self.assertRaises(ValidationError, no_title_organizer.save())
