from django.db import models
from decimal import Decimal, getcontext
from customers.models import Customer

class Loan(models.Model):
    loan_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.IntegerField()  # in months
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)  # percentage
    monthly_repayment = models.DecimalField(max_digits=12, decimal_places=2)  # EMI
    emis_paid_on_time = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'loans'

    def __str__(self):
        return f"Loan {self.loan_id} - {self.customer.full_name}"

    @property
    def repayments_left(self):
        """Calculate remaining EMIs"""
        if not self.is_active:
            return 0
        total_emis = self.tenure
        paid_emis = self.emis_paid_on_time
        return max(0, total_emis - paid_emis)

    def calculate_monthly_installment(self):
        """Calculate monthly installment using compound interest formula with Decimal"""
        getcontext().prec = 10  # Set precision for Decimal operations

        principal = self.loan_amount
        annual_rate = self.interest_rate / Decimal('100')  # Convert to decimal
        monthly_rate = annual_rate / Decimal('12')         # Monthly interest rate

        if monthly_rate == 0:
            return round(principal / self.tenure, 2)

        numerator = principal * monthly_rate * (1 + monthly_rate) ** self.tenure
        denominator = ((1 + monthly_rate) ** self.tenure) - 1

        emi = numerator / denominator
        return round(emi, 2)
