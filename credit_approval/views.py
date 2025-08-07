from django.db import models
from rest_framework import generics, status
from rest_framework.response import Response
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer, LoanDetailSerializer, LoanViewSerializer
from django.utils import timezone
from datetime import timedelta

# --- HELPER FUNCTION FOR ELIGIBILITY LOGIC ---
def check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure):
    try:
        customer = Customer.objects.get(pk=customer_id)
    except Customer.DoesNotExist:
        return {"error": "Customer not found", "status_code": status.HTTP_404_NOT_FOUND}

    # --- Credit Score Calculation ---
    credit_score = 0
    past_loans = Loan.objects.filter(customer=customer)
    num_loans_taken = past_loans.count()

    # 1. Past loans paid on time
    if num_loans_taken > 0:
        loans_paid_off = past_loans.filter(emis_paid_on_time__gte=models.F('tenure')).count()
        credit_score += (loans_paid_off / num_loans_taken) * 25

    # 2. Number of loans taken in the past
    credit_score += max(0, 20 - (num_loans_taken * 5))

    # 3. Loan activity in the current year
    current_year = timezone.now().year
    loans_this_year = past_loans.filter(date_of_approval__year=current_year).count()
    credit_score += max(0, 20 - (loans_this_year * 5))

    # 4. Total current debt vs approved limit
    if customer.current_debt > customer.approved_limit:
        credit_score = 0 # Immediately fail if debt exceeds limit
    else:
        credit_score += 35 # Base points for being within limit

    # --- Loan Approval Logic ---
    approval = False
    corrected_interest_rate = interest_rate
    if credit_score > 50:
        approval = True
    elif 30 < credit_score <= 50:
        approval = True
        corrected_interest_rate = max(interest_rate, 12.0)
    elif 10 < credit_score <= 30:
        approval = True
        corrected_interest_rate = max(interest_rate, 16.0)

    # Final check: Sum of all current EMIs should not be > 50% of monthly salary
    current_loans = past_loans.filter(end_date__gte=timezone.now().date())
    total_current_emis = sum(loan.monthly_payment for loan in current_loans)
    if total_current_emis > (customer.monthly_salary / 2):
        approval = False

    # --- EMI Calculation ---
    monthly_installment = 0
    if approval:
        if tenure > 0:
            r = corrected_interest_rate / 12 / 100
            monthly_installment = (loan_amount * r * (1 + r)**tenure) / ((1 + r)**tenure - 1) if r > 0 else (loan_amount / tenure)
        else:
            approval = False

    return {
        'customer_id': customer_id, 'credit_score': round(credit_score), 'approval': approval,
        'interest_rate': interest_rate, 'corrected_interest_rate': round(corrected_interest_rate, 2) if approval else None,
        'tenure': tenure, 'monthly_installment': round(monthly_installment, 2) if approval else None
    }


# --- REFACTORED VIEWS ---

class RegisterCustomer(generics.CreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def create(self, request, *args, **kwargs):
        monthly_salary = int(request.data.get('monthly_salary', 0))
        approved_limit = round(36 * monthly_salary, -5)

        data = request.data.copy()
        data['approved_limit'] = approved_limit
        data['current_debt'] = 0

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        customer = Customer.objects.get(pk=serializer.data['customer_id'])
        response_serializer = CustomerSerializer(customer)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CheckEligibility(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        customer_id = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount', 0))
        interest_rate = float(request.data.get('interest_rate', 0))
        tenure = int(request.data.get('tenure', 0))

        result = check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure)

        if "error" in result:
            return Response({"error": result["error"]}, status=result.get("status_code", 400))

        return Response(result)


class CreateLoan(generics.CreateAPIView):
    serializer_class = LoanSerializer

    def create(self, request, *args, **kwargs):
        customer_id = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount', 0))
        interest_rate = float(request.data.get('interest_rate', 0))
        tenure = int(request.data.get('tenure', 0)) # Corrected line

        eligibility_data = check_loan_eligibility(customer_id, loan_amount, interest_rate, tenure)

        if not eligibility_data.get('approval'):
            return Response({"message": "Loan not approved based on eligibility check.", "details": eligibility_data}, status=status.HTTP_400_BAD_REQUEST)

        customer = Customer.objects.get(pk=customer_id)

        approval_date = timezone.now().date()
        end_date = approval_date + timedelta(days=tenure * 30)

        loan_data = {
            "customer": customer.pk, "loan_amount": loan_amount, "tenure": tenure,
            "interest_rate": eligibility_data['corrected_interest_rate'],
            "monthly_payment": eligibility_data['monthly_installment'],
            "emis_paid_on_time": 0, "date_of_approval": approval_date, "end_date": end_date
        }

        serializer = self.get_serializer(data=loan_data)
        serializer.is_valid(raise_exception=True)
        loan = serializer.save()

        customer.current_debt += loan_amount
        customer.save()

        return Response({
            "loan_id": loan.loan_id, "customer_id": customer.customer_id,
            "loan_approved": True, "message": "Loan approved and created successfully",
            "monthly_installment": loan.monthly_payment
        }, status=status.HTTP_201_CREATED)


class ViewLoan(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanDetailSerializer
    lookup_field = 'loan_id'


class ViewCustomerLoans(generics.ListAPIView):
    serializer_class = LoanViewSerializer

    def get_queryset(self):
        customer_id = self.kwargs['customer_id']
        return Loan.objects.filter(customer__customer_id=customer_id)