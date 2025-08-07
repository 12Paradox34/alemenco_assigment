from rest_framework import serializers
from .models import Customer, Loan

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

class LoanDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer()

    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_payment', 'tenure', 'customer']

class LoanViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_payment', 'repayments_left']

    repayments_left = serializers.SerializerMethodField()

    def get_repayments_left(self, obj):
        from datetime import date
        today = date.today()
        end_date = obj.end_date
        repayments = (end_date.year - today.year) * 12 + (end_date.month - today.month)
        return max(0, repayments)