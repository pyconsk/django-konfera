from django.core.management.base import BaseCommand

from payments.utils import show_unpaid_orders


class Command(BaseCommand):
    help = 'Display all orders that needs to be notified, since they are not paid and are after due date.'

    def handle(self, *args, **options):
        orders_no, tickets_no = show_unpaid_orders(verbose=options['verbosity'])

        if options['verbosity'] > 0:
            self.stdout.write(
                self.style.SUCCESS('%s orders with %s tickets needs to be notified.' % (orders_no, tickets_no))
            )
