# Credit Approval System

A Django-based credit approval system that processes loan applications based on customer credit scores and historical data.

## Features

- Customer registration with automatic approved limit calculation
- Loan eligibility checking based on credit score
- Loan creation and management
- Historical data import from Excel files
- Background task processing with Celery
- RESTful API endpoints

## API Endpoints

1. **POST /register/** - Register a new customer
2. **POST /check-eligibility/** - Check loan eligibility
3. **POST /create-loan/** - Create a new loan
4. **GET /view-loan/{loan_id}/** - View loan details
5. **GET /view-loans/{customer_id}/** - View all loans for a customer

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Docker

   ```

### Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Import initial data**
   ```bash
   docker-compose exec web python manage.py import_data
   ```

## API Usage Examples

### Register a Customer
```bash
curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "age": 30,
    "monthly_income": 50000,
    "phone_number": "1234567890"
  }'
```

### Check Loan Eligibility
```bash
curl -X POST http://localhost:8000/check-eligibility/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 12.5,
    "tenure": 12
  }'
```

### Create a Loan
```bash
curl -X POST http://localhost:8000/create-loan/ \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 100000,
    "interest_rate": 12.5,
    "tenure": 12
  }'
```

### View Loan Details
```bash
curl http://localhost:8000/view-loan/1/
```

### View Customer Loans
```bash
curl http://localhost:8000/view-loans/1/
```

## Credit Score Calculation

The system calculates credit scores based on:
- Past loans paid on time (30 points)
- Number of loans taken in past (25 points)
- Loan activity in current year (25 points)
- Loan approved volume (20 points)

## Loan Approval Criteria

- Credit score > 50: Approve with interest rate ≥ 12%
- Credit score 30-50: Approve with interest rate > 12%
- Credit score 10-30: Approve with interest rate > 16%
- Credit score ≤ 10: No approval
- Current EMIs > 50% of monthly salary: No approval
- Loan amount + current debt > approved limit: No approval

## Project Structure

```
credit_system/
├── credit_system/          # Main project settings
├── customers/              # Customer management app
├── loans/                  # Loan management app
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## Technologies Used

- Django 4+
- Django REST Framework
- PostgreSQL
- Celery (background tasks)
- Redis (message broker)
- Pandas (data processing)
- Docker (containerization) 