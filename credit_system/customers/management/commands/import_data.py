from django.core.management.base import BaseCommand
from customers.tasks import import_customer_data
from loans.tasks import import_loan_data

class Command(BaseCommand):
    help = 'Import customer and loan data from Excel files'

    def handle(self, *args, **options):
        self.stdout.write('Starting data import...')
        
        # Import customer data synchronously
        self.stdout.write('Importing customer data...')
        customer_result = import_customer_data()
        self.stdout.write(f'Customer import result: {customer_result}')
        
        # Import loan data synchronously
        self.stdout.write('Importing loan data...')
        loan_result = import_loan_data()
        self.stdout.write(f'Loan import result: {loan_result}')
        
        self.stdout.write(self.style.SUCCESS('Data import completed!')) 