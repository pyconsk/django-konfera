import datetime

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from konfera import models
from konfera.models.discount_code import DiscountCode
from konfera.models.email_template import EmailTemplate
from konfera.models.event import Event
from konfera.models.order import Order
from konfera.models.speaker import Speaker
from konfera.models.sponsor import Sponsor
from konfera.models.talk import Talk
from konfera.models.ticket_type import TicketType
from .utils import random_string

now = timezone.now()
day = datetime.timedelta(days=1)
later = now + datetime.timedelta(hours=1)
distant_future = now + 3650 * day


class DiscountCodeTest(TestCase):
    fixtures = ['test_data.json']

    def test_string_representation(self):
        """
        String representation of model instance have to be equal to its title
        """
        dc = DiscountCode.objects.get(title='STU')
        self.assertEqual(str(dc), dc.title)

    def test_clean_dates(self):
        """
        Cleaning models dates follow different type of rules, also depending on event
        """
        tt = TicketType.objects.get(title='Student')
        dc = DiscountCode(title='Test Discount', hash='TSTSTSTSTST', ticket_type=tt)

        # Clean will prepopulate dates from ticket type
        dc.clean()
        self.assertEquals(dc.date_from, dc.ticket_type.date_from)
        self.assertEquals(dc.date_to, dc.ticket_type.date_to)

        # Discount can not be outside ticket type date range
        dc.date_from = dc.ticket_type.date_from - datetime.timedelta(minutes=5)
        self.assertRaises(ValidationError, dc.clean)
        dc.date_from = dc.ticket_type.date_from
        dc.date_to = dc.ticket_type.date_to + datetime.timedelta(minutes=5)
        self.assertRaises(ValidationError, dc.clean)

    def test_discount_values(self):
        """
        Discount is in percentage
        """
        dc = DiscountCode.objects.get(title='STU')
        dc.discount = 0
        dc.full_clean()
        dc.discount = 100
        dc.full_clean()
        dc.discount = -1
        self.assertRaises(ValidationError, dc.full_clean)
        dc.discount = 101
        self.assertRaises(ValidationError, dc.full_clean)


class EventTest(TestCase):
    fixtures = ['test_data.json']

    def test_string_representation(self):
        entry = models.Event(title="Test Event title")
        self.assertEqual(str(entry), entry.title)

    def test_dates(self):
        event = models.Event(title="Test Event dates")
        event.date_to = now
        event.date_from = later
        self.assertRaises(ValidationError, event.clean)

    def test_slug(self):
        title_length = Event._meta.get_field('title').max_length
        slug_length = Event._meta.get_field('slug').max_length
        self.assertGreaterEqual(slug_length, title_length)

        title = random_string(title_length)
        slug = slugify(title)
        date_from = now
        date_to = date_from + datetime.timedelta(seconds=1)
        location = models.Location.objects.order_by('?').first()
        event1 = Event(title=title, slug=slug, event_type=Event.MEETUP, date_from=date_from, date_to=date_to,
                       location=location, cfp_allowed=False)
        event1.save()
        self.assertEqual(Event.objects.get(slug=slug).title, title)

        event2 = Event(title=random_string(128, unicode=True), slug=slug, event_type=Event.MEETUP, date_from=date_from,
                       date_to=date_to, location=location, cfp_allowed=False)
        self.assertRaises(IntegrityError, event2.save)  # slug must be unique

    def test_cfp(self):
        event = Event(title='Test event', date_from=now, date_to=now + 2 * day, cfp_allowed=True)
        self.assertRaises(ValidationError, event.clean)
        event1 = Event(title='Test event', date_from=now, date_to=now + 2 * day, cfp_allowed=True, cfp_end=now)
        self.assertRaises(ValidationError, event1.clean)
        event2 = Event(title='Test normal event', date_from=now + 2 * day, date_to=now + 3 * day, cfp_end=now + day)
        self.assertIsNone(event2.clean())


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
        self.assertEqual(entry.status, Order.AWAITING)

    def test_paid_order_save(self):
        entry = models.Order(price=155.5, discount=5.5, status='paid')
        entry.save()
        self.assertIsNotNone(entry.payment_date)

    def test_to_pay(self):
        entry = models.Order(price=155.5, discount=5.5)
        self.assertEqual(entry.to_pay, 150)

    def test_left_to_pay(self):
        """ Attende paid less """
        entry = models.Order(price=155.5, discount=5.5, amount_paid=100)
        self.assertEqual(entry.left_to_pay, 50)

    def test_left_to_pay2(self):
        """ Attendee paid more """
        entry = models.Order(price=155.5, discount=5.5, amount_paid=200)
        self.assertEqual(entry.left_to_pay, 0)

    def test_order_event_with_ticket(self):
        entry = models.Order.objects.create(price=155.5, discount=5.5)
        # Create Event
        title = 'Test Event title'
        slug = slugify(title)
        date_from = timezone.now()
        date_to = date_from + datetime.timedelta(days=1)
        location = models.Location.objects.create(title="Test Location title")
        event = Event.objects.create(title=title, slug=slug, event_type=Event.MEETUP, date_from=date_from,
                                     date_to=date_to, location=location, status=Event.PUBLISHED, cfp_allowed=False)
        # Create TicketType for Event
        ticket_type = TicketType.objects.create(title='Test Ticket Type', price=150, event=event, date_from=date_from,
                                                date_to=date_to)
        # Create Ticket with TicketType
        models.Ticket.objects.create(title='Test Ticket', type=ticket_type, order=entry)
        self.assertEqual(entry.event, event)

    def test_order_event_without_ticket(self):
        entry = models.Order(price=155.5, discount=5.5)
        self.assertEqual(entry.event, None)


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
        date_from = timezone.now()
        date_to = date_from + datetime.timedelta(days=3)
        location = models.Location(title='test schedule location', street='test_street', city='test_city',
                                   postcode='000000', state='test_state', capacity=20)
        event = models.Event(title='test_event', description='test', event_type=Event.CONFERENCE,
                             status=Event.PUBLISHED, location=location, date_from=date_from, date_to=date_to)

        entry = models.Schedule(start=timezone.now(), duration=10, event=event)
        self.assertTrue(entry.full_clean)
        entry.duration = -1
        self.assertRaises(ValidationError, entry.full_clean)
        entry.duration = 301
        self.assertRaises(ValidationError, entry.full_clean)
        entry.duration = 300
        self.assertTrue(entry.full_clean)

    def test_event_daterange(self):
        date_from = timezone.now()
        date_to = date_from + datetime.timedelta(days=3)
        location = models.Location(title='test schedule location', street='test_street', city='test_city',
                                   postcode='000000', state='test_state', capacity=20)
        event = models.Event(title='test_event', description='test', event_type=Event.CONFERENCE,
                             status=Event.PUBLISHED, location=location, date_from=date_from, date_to=date_to)

        entry = models.Schedule(start=timezone.now(), duration=10, event=event)
        self.assertTrue(entry.full_clean)

        entry = models.Schedule(start=date_from - datetime.timedelta(days=1), duration=10, event=event)
        self.assertRaises(ValidationError, entry.full_clean)

        entry = models.Schedule(start=date_from + datetime.timedelta(days=10), duration=10, event=event)
        self.assertRaises(ValidationError, entry.full_clean)

    def test_talk_status(self):
        speaker = models.Speaker(first_name="Test", last_name="Scheduler")
        talk = models.Talk(title="Test Talk schedule", primary_speaker=speaker, status=Talk.DRAFT)
        entry = models.Schedule(start=timezone.now(), duration=0, talk=talk)
        self.assertRaises(ValidationError, entry.full_clean)
        talk.status = Talk.APPROVED
        self.assertTrue(entry.full_clean)


class SpeakerTest(TestCase):

    def test_string_representation(self):
        entry = models.Speaker(first_name="Test", last_name="Tester")
        self.assertEqual(str(entry), '%s %s' % (entry.first_name, entry.last_name))
        entry.title = 'mr'
        self.assertEqual(str(entry), '%s %s' % (entry.first_name, entry.last_name))

    def test_string_representation_title_mx(self):
        entry = models.Speaker(first_name="Test", last_name="Tester")
        self.assertEqual(str(entry), '%s %s' % (entry.first_name, entry.last_name))
        entry.title = 'mx'
        self.assertEqual(str(entry), '%s %s' % (entry.first_name, entry.last_name))


class SponsorTest(TestCase):
    fixtures = ['test_data.json']

    def test_string_representation(self):
        """
        String representation of model instance have to be equal to its title
        """
        sponsor = Sponsor.objects.get(title='Erigones')
        self.assertEqual(str(sponsor), sponsor.title)


class TalkTest(TestCase):
    fixtures = ['test_data.json']

    def test_string_representation(self):
        """
        String representation of model instance have to be equal to its title
        """
        talk = Talk.objects.get(title='How import works')
        self.assertEqual(str(talk), talk.title)

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


class TicketTest(TestCase):

    def setUp(self):
        location = models.Location(title='test_title', street='test_street', city='test_city', postcode='000000',
                                   country='test_country', capacity=20)
        location.save()
        event = models.Event(title='test_event', description='test', event_type='Event.meetup', cfp_allowed=False,
                             status=models.event.Event.PUBLISHED, location=location, date_from=now, date_to=later)
        event.save()
        self.ticket_type = models.TicketType(title='test', description='test', price=100, event=event,
                                             date_from=now, date_to=later)
        self.ticket_type.save()
        self.ticket_type_2 = models.TicketType(title='secondType', description='otherType', price=7, event=event,
                                               date_from=now, date_to=later)
        self.ticket_type_2.save()
        self.discount_code = models.DiscountCode(title='test discount', hash='test', discount=60,
                                                 date_from=now, date_to=later, usage=1, ticket_type=self.ticket_type)
        self.discount_code.save()
        self.discount_code_2 = models.DiscountCode(title='discount_2', hash='otherCode', discount=4, usage=100,
                                                   date_from=now, date_to=later, ticket_type=self.ticket_type_2)

    def test_string_representation(self):
        """
        String representation of model instance have to be equal to its title
        """
        entry = models.Ticket(first_name="Test", last_name="Tester")
        self.assertEqual(str(entry), '%s %s' % (entry.first_name, entry.last_name))

        entry.title = 'mr'
        self.assertEqual(
            str(entry),
            '%s %s %s' % (dict(Speaker.TITLE_CHOICES)[entry.title], entry.first_name, entry.last_name)
        )

    def test_automatic_order_generator(self):
        ticket = models.Ticket(status='requested', title='mr', first_name="test", last_name="Test",
                               type=self.ticket_type, email='test@test.com', phone='0912345678',
                               discount_code=self.discount_code)
        ticket.save()
        self.assertEquals(ticket.order.status, 'awaiting_payment')
        self.assertEquals(ticket.order.price, self.ticket_type.price)
        self.assertEquals(ticket.order.discount, 60)

    def test_clean_and_save_ticket_discount_code(self):
        # if saved with no discount_code, the ticket should save successfully
        ticket_no_code = models.Ticket(status='requested', title='mr', first_name="test", last_name="Test",
                                       type=self.ticket_type, email='test@test.com', phone='0912345678')
        ticket_no_code.save()

        # if saved with a code that matches the ticket type of the ticket, the ticket should save successfully
        ticket_with_valid_code = models.Ticket(status='requested', title='mr', first_name="test", last_name="Test",
                                               type=self.ticket_type, email='test@test.com', phone='0912345678',
                                               discount_code=self.discount_code)
        ticket_with_valid_code.save()
        # if discount code has been applied, the discount code should not be available
        self.assertEquals(self.discount_code.issued_tickets, 1)
        self.assertIs(self.discount_code.is_available, False)

        # if saved with a code that matches the ticket type of the ticket, the ticket should save successfully
        ticket_with_used_code = models.Ticket(status='requested', title='mr', first_name="test", last_name="Test",
                                              type=self.ticket_type, email='test@test.com', phone='0912345678',
                                              discount_code=self.discount_code)
        self.assertRaises(ValidationError, ticket_with_used_code.save)

        # if saved with a code that does not match the ticket type of the ticket, the ticket should
        # raise a validationError
        ticket_with_invalid_code = models.Ticket(status='requested', title='mr', first_name="test", last_name="Test",
                                                 type=self.ticket_type, email='test@test.com', phone='0912345678',
                                                 discount_code=self.discount_code_2)
        # the discount code has not been applied so the number of allowed usages should stay 100
        self.assertEquals(self.discount_code_2.issued_tickets, 0)
        self.assertRaises(ValidationError, ticket_with_invalid_code.save)

    def test_save_tickets_for_different_event(self):
        title1 = 'First title'
        title2 = 'Second title'
        date_from = now
        date_to = later
        location = models.Location.objects.order_by('?').first()
        date_kwargs = {'date_from': date_from, 'date_to': date_to}
        event_kwargs = {'event_type': Event.MEETUP, 'location': location, 'cfp_allowed': False}
        event_kwargs.update(date_kwargs)
        event1 = Event.objects.create(title=title1, slug=slugify(title1), **event_kwargs)
        event2 = Event.objects.create(title=title2, slug=slugify(title2), **event_kwargs)
        ticket_type1 = TicketType.objects.create(title=title1, event=event1, price=0, **date_kwargs)
        ticket_type2 = TicketType.objects.create(title=title2, event=event2, price=0, **date_kwargs)
        ticket_kwargs = {'status': 'requested', 'title': 'mr', 'first_name': 'test', 'last_name': 'Test',
                         'email': 'test@test.com', 'phone': '0912345678'}
        ticket1 = models.Ticket.objects.create(type=ticket_type1, **ticket_kwargs)
        ticket2 = models.Ticket(type=ticket_type2, order=ticket1.order, **ticket_kwargs)
        self.assertRaises(ValidationError, ticket2.save)


class TicketTypeTest(TestCase):
    fixtures = ['test_data.json']

    def test_string_representation(self):
        """
        String representation of model instance have to be equal to its title
        """
        tt = TicketType.objects.get(title='Standard Last Moment')
        self.assertEqual(str(tt), tt.title)

    def test_clean_dates(self):
        """
        Cleaning models dates follow different type of rules, also depending on event
        """
        event = Event.objects.get(title='PyCon SK 2016')  # PyCon SK 2016 is in the past
        tt = TicketType(title='Test Ticket', price=12, event=event)

        # Past event and no dates raises error
        self.assertRaises(ValidationError, tt.clean)

        # Past event and dates after it raises error
        tt.date_from = now
        tt.date_to = now + 3 * day
        self.assertRaises(ValidationError, tt.clean)
        tt.date_from = parse_datetime('2016-01-11T09:00:00Z')
        self.assertRaises(ValidationError, tt.clean)

        # End date can not be before start date
        tt.date_to = tt.date_from - 3 * day
        self.assertRaises(ValidationError, tt.clean)

        # Correct data in the past before event, SAVE.
        tt.date_to = tt.date_from + 9 * day
        tt.clean()
        tt.save()

        # PyCon SK 2054 is in the future
        future_event = Event.objects.create(
            title='PyCon SK 2054', description='test', event_type=Event.MEETUP, status=Event.PUBLISHED,
            location=event.location, cfp_end=distant_future - 7 * day,
            date_from=distant_future, date_to=distant_future + 7 * day)
        ftt = TicketType(title='Test Future Ticket', price=120, event=future_event)

        # Future event pre-populate the dates
        ftt.clean()
        self.assertEquals(abs(ftt.date_from - timezone.now()).seconds, 0)
        self.assertEquals(abs(ftt.date_to - ftt.event.date_to).seconds, 0)
        ftt.save()

    def test_status(self):
        now = timezone.now()
        event = Event.objects.get(title='PyCon SK 2016')  # PyCon SK 2016 is in the past
        tt = TicketType(title='Test Ticket', price=12, event=event)

        # Dates are not set or are in future ticket type is not available
        self.assertEquals(tt.status, TicketType.STATUSES[TicketType.NOT_AVAILABLE])
        tt.date_from = now + day
        self.assertEquals(tt.status, TicketType.STATUSES[TicketType.NOT_AVAILABLE])
        tt.date_to = now + 3 * day
        self.assertEquals(tt.status, TicketType.STATUSES[TicketType.NOT_AVAILABLE])

        # ticket type is within the date range so it is TicketType.active
        tt.date_from = now - day
        self.assertEquals(tt.status, TicketType.STATUSES[TicketType.ACTIVE])

        tt.usage = 0
        self.assertEquals(tt.status, TicketType.STATUSES[TicketType.SOLDOUT])

        # passed ticket types we consider as TicketType.expired
        tt.date_from = now - 3 * day
        tt.date_to = now - day
        self.assertEquals(tt.status, TicketType.STATUSES[TicketType.EXPIRED])


class OrganizerTest(TestCase):

    def setUp(self):
        self.first_organizer = models.Organizer(
            title='Mysterious Organizer', street='1 Up street', city='Big City', company_id='123',
            about_us="World famous yet unknown conference organizer."
        )

    def test_save(self):
        self.assertEquals(self.first_organizer.save(), None)
        noname_organizer = models.Organizer(street='2 Random', city='Small City')
        self.assertRaises(ValidationError, noname_organizer.save())

    def test_title(self):
        self.assertEquals(str(self.first_organizer), 'Mysterious Organizer')


class EmailTemplateTest(TestCase):
    def setUp(self):
        self.new_template = EmailTemplate.objects.create(
            name='New Template', text_template='Hello', html_template='Hello<br/>'
        )

    def test_template(self):
        et = EmailTemplate.objects.get(name='register_email')
        self.assertTrue(hasattr(et, 'text_template'))
        self.assertIn('Looking forward to seeing you.', et.text_template)
        self.assertEquals(str(et), 'register_email')

    def test_save(self):
        self.new_template.text_template = 'Hello world'
        self.new_template.save()
        new = EmailTemplate.objects.filter(name='New Template')
        self.assertTrue(new.exists())
        et = new[0]
        self.assertEquals(et.text_template, 'Hello world')
        self.assertEquals(et.html_template, 'Hello<br/>')

    def test_counter(self):
        self.assertEquals(self.new_template.counter, 0)
        self.new_template.add_count()
        self.assertEquals(self.new_template.counter, 1)
