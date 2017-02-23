from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from konfera.models import Ticket, Talk, Order, TicketType


class Command(BaseCommand):
    help = 'Generate tickets for speakers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--event',
            nargs='?',
            dest='event',
            help='Define event in which tickets will be generated.',
        )

    @staticmethod
    def create_ticket(speaker, speaker_ticket_type):
        ticket = Ticket(first_name=speaker.first_name, last_name=speaker.last_name, status=Ticket.REGISTERED,
                        email=speaker.email, type=speaker_ticket_type)
        ticket.save()

        ticket.order.status = Order.PAID
        ticket.order.save()

    def search_and_crete_ticket(self, speaker, speaker_ticket_type, options):
        if not Ticket.objects.filter(last_name=speaker.last_name):
            if options['verbosity'] > 1:
                self.stdout.write('Speaker: %s has not been found in DB. Trying to create...' % speaker)
            self.create_ticket(speaker, speaker_ticket_type)

            if options['verbosity'] > 0:
                self.stdout.write(self.style.SUCCESS('Speaker: %s ticket created.' % speaker))
        elif options['verbosity'] > 0:
            self.stdout.write(self.style.WARNING('Speaker: %s has ticket.' % speaker))

    def handle(self, *args, **options):
        event = options.get('event', False)

        if event:
            try:
                speaker_ticket_type = TicketType.objects.filter(attendee_type=TicketType.SPEAKER)\
                    .get(event__title=event)
            except ObjectDoesNotExist:
                self.stdout.write(self.style.ERROR('Event not found.'))
                return
        else:
            self.stdout.write(self.style.ERROR('Event not defined.'))
            return

        for talk in Talk.objects.filter(status__in=(Talk.APPROVED, Talk.PUBLISHED)).filter(event__title=event):
            if talk.primary_speaker:
                self.search_and_crete_ticket(talk.primary_speaker, speaker_ticket_type, options)

            if talk.secondary_speaker:
                self.search_and_crete_ticket(talk.secondary_speaker, speaker_ticket_type, options)

        if options['verbosity'] > 0:
            self.stdout.write(self.style.SUCCESS('Successfully generated speakers tickets.'))
