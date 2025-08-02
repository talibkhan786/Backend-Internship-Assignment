import pandas as pd
from decimal import Decimal
from datetime import datetime
from django.conf import settings
import os
from .models import Loan
from customers.models import Customer

# Try to import Celery, if not available, create a dummy decorator
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    def shared_task(func):
        return func

@shared_task
def import_loan_data():
    """Import loan data from Excel file"""
    try:
        # Path to the Excel file
        excel_path = os.path.join(settings.BASE_DIR, 'loan_data.xlsx')
        
        # Read Excel file
        df = pd.read_excel(excel_path)
        
        # Normalize column names: lower case, replace spaces with underscores
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        # Process each row
        for _, row in df.iterrows():
            try:
                # Get customer
                customer = Customer.objects.get(customer_id=row['customer_id'])
                
                # Check if loan already exists
                if not Loan.objects.filter(loan_id=row['loan_id']).exists():
                    # Parse dates from 'date_of_approval' and 'end_date'
                    start_date = pd.to_datetime(row['date_of_approval']).date()
                    end_date = pd.to_datetime(row['end_date']).date()
                    
                    Loan.objects.create(
                        loan_id=row['loan_id'],
                        customer=customer,
                        loan_amount=Decimal(str(row['loan_amount'])),
                        tenure=row['tenure'],
                        interest_rate=Decimal(str(row['interest_rate'])),
                        monthly_repayment=Decimal(str(row['monthly_payment'])),
                        emis_paid_on_time=row['emis_paid_on_time'],
                        start_date=start_date,
                        end_date=end_date,
                        is_active=True
                    )
                    
            except Customer.DoesNotExist:
                print(f"Customer {row['customer_id']} not found for loan {row['loan_id']}")
                continue
        
        return f"Successfully imported {len(df)} loans"
        
    except Exception as e:
        return f"Error importing loan data: {str(e)}"
