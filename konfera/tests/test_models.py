import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from konfera import models
from konfera.models.speaker import TITLE_CHOICES
from konfera.models.order import AWAITING


class DiscountCodeTest(TestCase):

    def test_string_representation(self):
        entry = models.DiscountCode(title="Test DiscountCode title")
        self.assertEqual(str(entry), entry.title)


class EventTest(TestCase):

    def test_string_representation(self):
        entry = models.Event(title="Test Event title")
        self.assertEqual(str(entry), entry.title)

    def test_dates_from_to(self):
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
        location = models.Location(title='test_title', street='test_street', city='test_city', postcode=000000,
                                   state='test_state', capacity=20)
        location.save()
        event = models.Event(title='test_event', description='test', event_type='meetup', status='published',
                             location=location, date_from=timezone.now(), date_to=timezone.now())
        event.save()
        ticket_type = models.TicketType(title='test', description='test', price=100, event=event,
                                        date_from=timezone.now(), date_to=timezone.now())
        ticket_type.save()
        discount_code = models.DiscountCode(title='test discount', hash='test', discount=60,
                                            available_from=timezone.now(), available_to=timezone.now(), usage=1,
                                            ticket_type=ticket_type)
        discount_code.save()
        ticket = models.Ticket(status='requested', title='mr', first_name="test", last_name="Test", type=ticket_type,
                               email='test@test.com', phone='0912345678', description='test',
                               discount_code=discount_code)
        ticket.save()
        self.assertEquals(ticket.order.status, 'awaiting_payment')
        self.assertEquals(ticket.order.price, ticket_type.price)
        self.assertEquals(ticket.order.discount, 60)


class TicketTypeTest(TestCase):

    def test_string_representation(self):
        entry = models.TicketType(title="Test TicketType title")
        self.assertEqual(str(entry), entry.title)

    def test_dates_from_to(self):
        tt = models.TicketType(title="Test TicketType dates")
        tt.date_to = timezone.now()
        tt.date_from = tt.date_to + datetime.timedelta(+3)
        self.assertRaises(ValidationError, tt.clean)
