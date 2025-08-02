from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from customers.models import Customer
from .models import Loan
from .serializers import (
    CheckEligibilitySerializer, CheckEligibilityResponseSerializer,
    CreateLoanSerializer, CreateLoanResponseSerializer,
    ViewLoanResponseSerializer, ViewLoansResponseSerializer
)
from .services import LoanEligibilityService
from datetime import datetime, timedelta

# Create your views here.

@api_view(['POST'])
def check_eligibility(request):
    """Check loan eligibility for a customer"""
    serializer = CheckEligibilitySerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        result = LoanEligibilityService.check_eligibility(
            data['customer_id'],
            data['loan_amount'],
            data['interest_rate'],
            data['tenure']
        )
        
        response_serializer = CheckEligibilityResponseSerializer(result)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def create_loan(request):
    """Create a new loan based on eligibility"""
    serializer = CreateLoanSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Check eligibility first
        eligibility_result = LoanEligibilityService.check_eligibility(
            data['customer_id'],
            data['loan_amount'],
            data['interest_rate'],
            data['tenure']
        )
        
        if not eligibility_result['approval']:
            response_data = {
                'loan_id': None,
                'customer_id': data['customer_id'],
                'loan_approved': False,
                'message': eligibility_result['message'],
                'monthly_installment': None
            }
            response_serializer = CreateLoanResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the loan
        try:
            customer = Customer.objects.get(customer_id=data['customer_id'])
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=data['loan_amount'],
                tenure=data['tenure'],
                interest_rate=eligibility_result['corrected_interest_rate'],
                monthly_repayment=eligibility_result['monthly_installment'],
                start_date=datetime.now().date(),
                end_date=(datetime.now() + timedelta(days=data['tenure'] * 30)).date()
            )
            
            response_data = {
                'loan_id': loan.loan_id,
                'customer_id': data['customer_id'],
                'loan_approved': True,
                'message': 'Loan approved successfully',
                'monthly_installment': loan.monthly_repayment
            }
            response_serializer = CreateLoanResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Customer.DoesNotExist:
            response_data = {
                'loan_id': None,
                'customer_id': data['customer_id'],
                'loan_approved': False,
                'message': 'Customer not found',
                'monthly_installment': None
            }
            response_serializer = CreateLoanResponseSerializer(response_data)
            return Response(response_serializer.data, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def view_loan(request, loan_id):
    """View loan details by loan ID"""
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        
        response_data = {
            'loan_id': loan.loan_id,
            'customer': {
                'customer_id': loan.customer.customer_id,
                'first_name': loan.customer.first_name,
                'last_name': loan.customer.last_name,
                'phone_number': loan.customer.phone_number,
                'age': loan.customer.age
            },
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_repayment,
            'tenure': loan.tenure
        }
        
        response_serializer = ViewLoanResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
        
    except Loan.DoesNotExist:
        return Response(
            {'error': 'Loan not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
def view_customer_loans(request, customer_id):
    """View all loans for a customer"""
    try:
        customer = Customer.objects.get(customer_id=customer_id)
        loans = Loan.objects.filter(customer=customer, is_active=True)
        
        loans_data = []
        for loan in loans:
            loan_data = {
                'loan_id': loan.loan_id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_repayment,
                'repayments_left': loan.repayments_left
            }
            loans_data.append(loan_data)
        
        return Response(loans_data, status=status.HTTP_200_OK)
        
    except Customer.DoesNotExist:
        return Response(
            {'error': 'Customer not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
