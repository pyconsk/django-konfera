from django.core.management.base import BaseCommand

from payments.utils import show_overdue_orders


class Command(BaseCommand):
    help = 'Display all orders that are overdue, and will be expired.'

    def handle(self, *args, **options):
        orders_no, tickets_no = show_overdue_orders(verbose=options['verbosity'])

        if options['verbosity'] > 0:
            self.stdout.write(
                self.style.SUCCESS('%s orders with %s tickets are overdue.' % (orders_no, tickets_no))
            )
