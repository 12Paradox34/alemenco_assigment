import pandas as pd
from django.core.management.base import BaseCommand
from credit_approval.models import Customer, Loan
from datetime import datetime

class Command(BaseCommand):
    help = 'Ingest data from Excel files into the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data ingestion...'))

        # Ingest Customer Data
        try:
            customer_df = pd.read_csv('customer_data.csv')
            for _, row in customer_df.iterrows():
                Customer.objects.update_or_create(
                    customer_id=row['Customer ID'],
                    defaults={
                        'first_name': row['First Name'],
                        'last_name': row['Last Name'],
                        'age': row['Age'],
                        'phone_number': row['Phone Number'],
                        'monthly_salary': row['Monthly Salary'],
                        'approved_limit': row['Approved Limit'],
                    }
                )
            self.stdout.write(self.style.SUCCESS('Successfully ingested customer data.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('customer_data.xlsx - Sheet1.csv not found.'))

        # Ingest Loan Data
        try:
            loan_df = pd.read_csv('loan_data.csv')
            for _, row in loan_df.iterrows():
                try:
                    customer = Customer.objects.get(customer_id=row['Customer ID'])
                    Loan.objects.update_or_create(
                        loan_id=row['Loan ID'],
                        defaults={
                            'customer': customer,
                            'loan_amount': row['Loan Amount'],
                            'tenure': row['Tenure'],
                            'interest_rate': row['Interest Rate'],
                            'monthly_payment': row['Monthly payment'],
                            'emis_paid_on_time': row['EMIs paid on Time'],
                            # --- FIX IS HERE ---
                            'date_of_approval': datetime.strptime(str(row['Date of Approval']), '%m/%d/%Y').date(),
                            'end_date': datetime.strptime(str(row['End Date']), '%m/%d/%Y').date(),
                            # --------------------
                        }
                    )
                except Customer.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Customer with ID {row['Customer ID']} not found for loan {row['Loan ID']}."))
            self.stdout.write(self.style.SUCCESS('Successfully ingested loan data.'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('loan_data.xlsx - Sheet1.csv not found.'))