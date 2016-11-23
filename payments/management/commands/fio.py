from django.core.management.base import BaseCommand

from payments.utils import check_payments_status


class Command(BaseCommand):
    help = 'Process payments in FIO Bank.'

    def handle(self, *args, **options):
        check_payments_status()
        self.stdout.write(self.style.SUCCESS('Successfully processed awaiting and partly paid orders'))
