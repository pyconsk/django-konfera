from django.test import TestCase

from konfera import models
from konfera.models.speaker import TITLE_CHOICES


class DiscountCodesTest(TestCase):

    def test_string_representation(self):
        entry = models.DiscountCodes(title="Test DiscountCode title")
        self.assertEqual(str(entry), entry.title)


class EventTest(TestCase):

    def test_string_representation(self):
        entry = models.Event(title="Test Event title")
        self.assertEqual(str(entry), entry.title)


class LocationTest(TestCase):

    def test_string_representation(self):
        entry = models.Location(title="Test Location title")
        self.assertEqual(str(entry), entry.title)


class OrderTest(TestCase):

    def test_string_representation(self):
        entry = models.Order(price=155.5, discount=5.5)
        self.assertEqual(str(entry), str(entry.price - entry.discount))


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


class TicketTypeTest(TestCase):

    def test_string_representation(self):
        entry = models.TicketType(title="Test TicketType title")
        self.assertEqual(str(entry), entry.title)
