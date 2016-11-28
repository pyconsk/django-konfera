from django.core.management.base import BaseCommand, CommandError

from payments.utils import check_payments_status

from fiobank import ThrottlingError


class Command(BaseCommand):
    help = 'Process payments in FIO Bank.'

    def handle(self, *args, **options):
        try:
            check_payments_status(verbose=options['verbosity'])
        except ThrottlingError:
            raise CommandError('Command should be used only once per 30s.')

        if options['verbosity'] > 0:
            self.stdout.write(self.style.SUCCESS('Successfully processed awaiting and partly paid orders'))
