from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Customer
from .serializers import RegisterCustomerSerializer, RegisterCustomerResponseSerializer

@api_view(['POST'])
def register_customer(request):
    """Register a new customer"""
    serializer = RegisterCustomerSerializer(data=request.data)
    if serializer.is_valid():
        # Calculate approved limit
        monthly_salary = serializer.validated_data['monthly_salary']
        approved_limit = round(monthly_salary * 36 / 100000) * 100000  # Round to nearest lakh
        
        # Create customer
        customer = Customer.objects.create(
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            age=serializer.validated_data['age'],
            phone_number=serializer.validated_data['phone_number'],
            monthly_salary=monthly_salary,
            approved_limit=approved_limit
        )
        
        # Prepare response
        response_data = {
            'customer_id': customer.customer_id,
            'name': f"{customer.first_name} {customer.last_name}",
            'age': customer.age,
            'monthly_salary': customer.monthly_salary,
            'approved_limit': customer.approved_limit,
            'phone_number': customer.phone_number
        }
        
        response_serializer = RegisterCustomerResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
