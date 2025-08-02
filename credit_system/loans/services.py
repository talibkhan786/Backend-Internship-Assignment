from decimal import Decimal
from datetime import datetime, date
from django.db.models import Sum, Count
from customers.models import Customer
from .models import Loan

class CreditScoreService:
    @staticmethod
    def calculate_credit_score(customer_id):
        """Calculate credit score based on historical loan data"""
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return 0

        # Get all loans for the customer
        loans = Loan.objects.filter(customer=customer)
        
        if not loans.exists():
            return 0

        # Check if current debt exceeds approved limit
        current_debt = loans.filter(is_active=True).aggregate(
            total_debt=Sum('loan_amount')
        )['total_debt'] or Decimal('0')
        
        if current_debt > customer.approved_limit:
            return 0

        # Calculate credit score components
        score = 0
        
        # 1. Past loans paid on time (30 points)
        total_emis_paid = sum(loan.emis_paid_on_time for loan in loans)
        total_emis_expected = sum(loan.tenure for loan in loans)
        if total_emis_expected > 0:
            on_time_ratio = total_emis_paid / total_emis_expected
            score += min(30, int(on_time_ratio * 30))

        # 2. Number of loans taken in past (25 points)
        loan_count = loans.count()
        if loan_count >= 5:
            score += 25
        elif loan_count >= 3:
            score += 20
        elif loan_count >= 1:
            score += 15

        # 3. Loan activity in current year (25 points)
        current_year = datetime.now().year
        current_year_loans = loans.filter(start_date__year=current_year)
        if current_year_loans.exists():
            score += 25

        # 4. Loan approved volume (20 points)
        total_loan_volume = loans.aggregate(
            total_volume=Sum('loan_amount')
        )['total_volume'] or Decimal('0')
        
        if total_loan_volume >= Decimal('1000000'):  # 10 lakhs
            score += 20
        elif total_loan_volume >= Decimal('500000'):  # 5 lakhs
            score += 15
        elif total_loan_volume >= Decimal('100000'):  # 1 lakh
            score += 10

        return min(100, score)

class LoanEligibilityService:
    @staticmethod
    def check_eligibility(customer_id, loan_amount, interest_rate, tenure):
        """Check loan eligibility and return appropriate response"""
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            return {
                'customer_id': customer_id,
                'approval': False,
                'interest_rate': interest_rate,
                'corrected_interest_rate': interest_rate,
                'tenure': tenure,
                'monthly_installment': 0,
                'message': 'Customer not found'
            }

        # Calculate credit score
        credit_score = CreditScoreService.calculate_credit_score(customer_id)
        
        # Check current debt vs approved limit
        current_loans = Loan.objects.filter(customer=customer, is_active=True)
        current_debt = current_loans.aggregate(
            total_debt=Sum('loan_amount')
        )['total_debt'] or Decimal('0')
        
        if current_debt + loan_amount > customer.approved_limit:
            return {
                'customer_id': customer_id,
                'approval': False,
                'interest_rate': interest_rate,
                'corrected_interest_rate': interest_rate,
                'tenure': tenure,
                'monthly_installment': 0,
                'message': 'Loan amount exceeds approved limit'
            }

        # Check if current EMIs > 50% of monthly salary
        current_monthly_emis = current_loans.aggregate(
            total_emi=Sum('monthly_repayment')
        )['total_emi'] or Decimal('0')
        
        if current_monthly_emis > customer.monthly_salary * Decimal('0.5'):
            return {
                'customer_id': customer_id,
                'approval': False,
                'interest_rate': interest_rate,
                'corrected_interest_rate': interest_rate,
                'tenure': tenure,
                'monthly_installment': 0,
                'message': 'Current EMIs exceed 50% of monthly salary'
            }

        # Determine approval and interest rate based on credit score
        approval = False
        corrected_interest_rate = interest_rate
        
        if credit_score > 50:
            approval = True
            if interest_rate < 12:
                corrected_interest_rate = 12
        elif 30 < credit_score <= 50:
            if interest_rate > 12:
                approval = True
                corrected_interest_rate = max(interest_rate, 12)
            else:
                corrected_interest_rate = 12
        elif 10 < credit_score <= 30:
            if interest_rate > 16:
                approval = True
                corrected_interest_rate = max(interest_rate, 16)
            else:
                corrected_interest_rate = 16
        else:  # credit_score <= 10
            approval = False
            corrected_interest_rate = 16

        # Calculate monthly installment
        monthly_installment = 0
        if approval:
            # Create temporary loan object to calculate EMI
            temp_loan = Loan(
                loan_amount=loan_amount,
                interest_rate=corrected_interest_rate,
                tenure=tenure
            )
            monthly_installment = temp_loan.calculate_monthly_installment()

        return {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': monthly_installment,
            'message': 'Loan approved' if approval else 'Loan not approved based on credit score'
        } 