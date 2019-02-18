from django.core.management.base import BaseCommand, CommandError
from identity.utils import create_accounts_from_csv

class Command(BaseCommand):
    help = 'Creates accounts from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('-csv', required=True, 
                            help="csv file to import")
        parser.add_argument('-realm', required=False,
                            default='guest.unical.it',
                            help="csv file to import")
        parser.add_argument('-test', required=False, action="store_true", 
                            help="do not save imports, just test")
        parser.add_argument('-debug', required=False, action="store_true", 
                            help="see debug message")

    def handle(self, *args, **options):
        print(args, options)
        cnt = create_accounts_from_csv(csv_file=options['csv'],
                                 realm=options['realm'],
                                 test=options['test'],
                                 debug=options['debug'])
        self.stdout.write(self.style.SUCCESS('Successfully processed {} Accounts'.format(cnt)
                                            ))
