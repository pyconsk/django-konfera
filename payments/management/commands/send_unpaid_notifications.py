from django.core.management.base import BaseCommand

from payments.utils import send_unpaid_order_email_notifications


class Command(BaseCommand):
    help = 'Send notifications for unpaid order by emails'

    def handle(self, *args, **options):
        send_unpaid_order_email_notifications(verbose=options['verbosity'])

        if options['verbosity'] > 0:
            self.stdout.write(self.style.SUCCESS('Successfully sent unpaid order notifications.'))
