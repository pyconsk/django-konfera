from django.core.management.base import BaseCommand

from payments.utils import email_unpaid_orders


class Command(BaseCommand):
    help = 'Send email notifications for unpaid order.'

    def handle(self, *args, **options):
        email_unpaid_orders(verbose=options['verbosity'])

        if options['verbosity'] > 0:
            self.stdout.write(self.style.SUCCESS('Successfully sent email notifications for unpaid orders.'))
