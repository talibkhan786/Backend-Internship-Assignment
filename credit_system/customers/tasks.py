import pandas as pd
from decimal import Decimal
from django.conf import settings
import os
from .models import Customer

# Try to import Celery, if not available, create a dummy decorator
try:
    from celery import shared_task
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    def shared_task(func):
        return func

@shared_task
def import_customer_data():
    """Import customer data from Excel file"""
    try:
        # Path to the Excel file
        excel_path = os.path.join(settings.BASE_DIR, 'customer_data.xlsx')
        
        # Read Excel file
        df = pd.read_excel(excel_path)

        # Normalize column names: e.g., "Customer ID" -> "customer_id"
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]

        # Process each row
        for _, row in df.iterrows():
            # Check if customer already exists
            if not Customer.objects.filter(customer_id=row['customer_id']).exists():
                Customer.objects.create(
                    customer_id=row['customer_id'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    age=row.get('age', 25),  # Default age if not provided
                    phone_number=str(row['phone_number']),
                    monthly_salary=Decimal(str(row['monthly_salary'])),
                    approved_limit=Decimal(str(row['approved_limit'])),
                    current_debt=Decimal(str(row.get('current_debt', 0)))
                )
        
        return f"Successfully imported {len(df)} customers"
        
    except Exception as e:
        return f"Error importing customer data: {str(e)}" 