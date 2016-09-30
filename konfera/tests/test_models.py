import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from konfera import models
from konfera.models.speaker import TITLE_CHOICES
from konfera.models.order import AWAITING
from konfera.models.ticket_type import NOT_AVAILABLE, ACTIVE, EXPIRED


class Mockup(object):

    def __init__(self):
        # TODO: store data in DB!
        self.now = timezone.now()

        self.event = models.Event(
            title="UnitTest Event",
            date_from=self.now,
            date_to=self.now + datetime.timedelta(+1),
        )
#        self.event.save()

        self.ticket_type = models.TicketType(
            title="UnitTest TicketType for UnitTest Event",
            date_from=self.event.date_from,
            date_to=self.event.date_to,
            event=self.event,
        )
#        self.ticket_type.save()

        self.discount_code = models.DiscountCode(
            title="UnitTest DiscountCode for UnitTest TicketType",
            hash="TestHash",
            date_from=self.ticket_type.date_from,
            date_to=self.ticket_type.date_to,
            discount=0,
            ticket_type=self.ticket_type,
        )
#        self.ticket_type.save()


# TODO: Unify tests in fewer TestCases, so we construct test DB only once to make the tests run faster!
class DiscountCodeTest(TestCase):

    def setUp(self):
        self.mock = Mockup()

    def test_string_representation(self):
        entry = models.DiscountCode(title="Test DiscountCode title")
        self.assertEqual(str(entry), entry.title)

    def test_string_representation(self):
        """
        String representation of model instance have to be equal to its title
        """
        dc = self.mock.discount_code
        self.assertEqual(str(dc), dc.title)

    def test_dates_start_before_end(self):
        """
        Discount code have to have start before end
        """
        dc = self.mock.discount_code
        dc.date_from = dc.date_to + datetime.timedelta(+3)
        self.assertRaises(ValidationError, dc.clean)

    def test_dates_start_end_definition_from_ticket_type(self):
        """
        Discount code start and end are picked up from Ticket type if not defined
        """
        dc = self.mock.discount_code
        dc.date_from = None
        dc.date_to = None
        dc.clean()
        self.assertEqual(dc.date_from, dc.ticket_type.date_from)
        self.assertEqual(dc.date_to, dc.ticket_type.date_to)

    def test_dates_start_before_ticket_type_start(self):
        """
        Discount code can not start before Ticket type
        """
        dc = self.mock.discount_code
        dc.date_from = dc.ticket_type.date_from + datetime.timedelta(-3)
        self.assertRaises(ValidationError, dc.clean)

    def test_dates_end_after_ticket_type_end(self):
        """
        Discount code can not end after Ticket type
        """
        dc = self.mock.discount_code
        dc.date_to = dc.ticket_type.date_to + datetime.timedelta(+3)
        self.assertRaises(ValidationError, dc.clean)

    # def test_discount_values(self):
    #     """
    #     Discount is in percentage
    #     """
    #     dc = self.mock.discount_code
    #     dc.discount = 0
    #     print(dc.title, dc.ticket_type)
    #     dc.full_clean()
    #     dc.discount = 100
    #     dc.full_clean()
    #     dc.discount = -1
    #     self.assertRaises(ValidationError, dc.full_clean)
    #     dc.discount = 101
    #     self.assertRaises(ValidationError, dc.full_clean)

class EventTest(TestCase):

    def test_string_representation(self):
        entry = models.Event(title="Test Event title")
        self.assertEqual(str(entry), entry.title)

    def test_dates(self):
        event = models.Event(title="Test Event dates")
        event.date_to = timezone.now()
        event.date_from = event.date_to + datetime.timedelta(+3)
        self.assertRaises(ValidationError, event.clean)


class LocationTest(TestCase):

    def test_string_representation(self):
        entry = models.Location(title="Test Location title")
        self.assertEqual(str(entry), entry.title)


class OrderTest(TestCase):

    def test_string_representation(self):
        entry = models.Order(price=155.5, discount=5.5)
        self.assertEqual(str(entry), str(entry.price - entry.discount))

    def test_unpaid_order_save(self):
        entry = models.Order(price=155.5, discount=5.5)
        entry.save()
        self.assertIsNone(entry.payment_date)
        self.assertEqual(entry.status, AWAITING)

    def test_paid_order_save(self):
        entry = models.Order(price=155.5, discount=5.5, status='paid')
        entry.save()
        self.assertIsNotNone(entry.payment_date)


class ReceiptTest(TestCase):

    def test_string_representation(self):
        entry = models.Receipt(title="Test Receipt title")
        self.assertEqual(str(entry), entry.title)


class RoomModelTest(TestCase):

    def test_string_representation(self):
        entry = models.Room(title="My Room title")
        self.assertEqual(str(entry), entry.title)


class ScheduleTest(TestCase):

    def test_string_representation(self):
        entry = models.Schedule(start="2015-01-01 01:01:01", duration=15)
        self.assertEqual(str(entry), '%s (%s min)' % (entry.start, entry.duration))

    def test_duration_range(self):
        entry = models.Schedule(start="2015-01-01 01:01:01", duration=0)
        self.assertTrue(entry.full_clean)
        entry.duration = -1
        self.assertRaises(ValidationError, entry.full_clean)
        entry.duration = 301
        self.assertRaises(ValidationError, entry.full_clean)
        entry.duration = 300
        self.assertTrue(entry.full_clean)


class SpeakerTest(TestCase):

    def test_string_representation(self):
        entry = models.Speaker(first_name="Test", last_name="Tester")
        self.assertEqual(str(entry), '%s %s' % (entry.first_name, entry.last_name))
        entry.title = 'mr'
        self.assertEqual(
            str(entry),
            '%s %s %s' % (dict(TITLE_CHOICES)[entry.title], entry.first_name, entry.last_name)
        )


class SponsorTest(TestCase):

    def test_string_representation(self):
        entry = models.Sponsor(title="Test Sponsor title")
        self.assertEqual(str(entry), entry.title)


class TalkTest(TestCase):

    def test_different_speakers(self):
        speaker1 = models.Speaker(first_name="Test", last_name="Tester")
        speaker2 = models.Speaker(first_name="Test", last_name="Testovac")
        talk = models.Talk(title="Test Talk speakers")
        talk.primary_speaker = speaker1
        self.assertTrue(talk.clean)
        talk.secondary_speaker = speaker2
        self.assertTrue(talk.clean)
        talk.secondary_speaker = speaker1
        self.assertRaises(ValidationError, talk.clean)

    def test_string_representation(self):
        entry = models.Talk(title="Test Talk title")
        self.assertEqual(str(entry), entry.title)


class TicketTest(TestCase):

    def test_string_representation(self):
        entry = models.Ticket(first_name="Test", last_name="Tester")
        self.assertEqual(str(entry), '%s %s' % (entry.first_name, entry.last_name))
        entry.title = 'mr'
        self.assertEqual(
            str(entry),
            '%s %s %s' % (dict(TITLE_CHOICES)[entry.title], entry.first_name, entry.last_name)
        )

    def test_automatic_order_generator(self):
        time = timezone.now()
        location = models.Location(title='test_title', street='test_street', city='test_city', postcode=000000,
                                   state='test_state', capacity=20)
        location.save()
        event = models.Event(title='test_event', description='test', event_type='meetup',
                             status=models.event.PUBLISHED, location=location, date_from=time, date_to=time)
        event.save()
        ticket_type = models.TicketType(title='test', description='test', price=100, event=event,
                                        date_from=timezone.now(), date_to=timezone.now())
        ticket_type.save()
        discount_code = models.DiscountCode(title='test discount', hash='test', discount=60,
                                            available_from=time, available_to=time, usage=1,
                                            ticket_type=ticket_type)
        discount_code.save()
        ticket = models.Ticket(status='requested', title='mr', first_name="test", last_name="Test", type=ticket_type,
                               email='test@test.com', phone='0912345678', discount_code=discount_code)
        ticket.save()
        self.assertEquals(ticket.order.status, 'awaiting_payment')
        self.assertEquals(ticket.order.price, ticket_type.price)
        self.assertEquals(ticket.order.discount, 60)


class TicketTypeTest(TestCase):

    def setUp(self):
        self.mock = Mockup()

    def test_string_representation(self):
        """
        String representation of model instance have to be equal to its title
        """
        tt = self.mock.ticket_type
        self.assertEqual(str(tt), tt.title)

    def test_dates_start_before_end(self):
        """
        Ticket type have to have start before end
        """
        tt = self.mock.ticket_type
        tt.date_from = tt.date_to + datetime.timedelta(+3)
        self.assertRaises(ValidationError, tt.clean)

    def test_dates_start_after_event_end(self):
        """
        Ticket type can not start after event end
        """
        tt = self.mock.ticket_type
        tt.date_from = tt.event.date_to + datetime.timedelta(+3)
        self.assertRaises(ValidationError, tt.clean)

    def test_dates_end_after_event_end(self):
        """
        Ticket type can not end after event end
        """
        tt = self.mock.ticket_type
        tt.date_to = tt.event.date_to + datetime.timedelta(+3)
        self.assertRaises(ValidationError, tt.clean)

    def test_unavailable_ticket(self):
        tt = models.TicketType()
        tt.date_from = timezone.now() + datetime.timedelta(days=1)
        tt.date_to = timezone.now() + datetime.timedelta(days=3)
        self.assertEquals(tt.status(), NOT_AVAILABLE)

    def test_active_ticket(self):
        tt = models.TicketType()
        tt.date_from = timezone.now() - datetime.timedelta(days=1)
        tt.date_to = timezone.now() + datetime.timedelta(days=3)
        self.assertEquals(tt.status(), ACTIVE)

    def test_expired_ticket(self):
        tt = models.TicketType()
        tt.date_from = timezone.now() - datetime.timedelta(days=3)
        tt.date_to = timezone.now() - datetime.timedelta(days=1)
        self.assertEquals(tt.status(), EXPIRED)
