"""
Seed script — creates demo users and sample financial records.
Run: python seed.py
"""
import os
import django
import random
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User, Role
from records.models import FinancialRecord, RecordType, Category

# ── Users ────────────────────────────────────────────────────────────────────
print("Creating users...")
admin = User.objects.create_user(
    email='admin@finance.dev', password='Admin@1234',
    full_name='Alice Admin', role=Role.ADMIN
)
analyst = User.objects.create_user(
    email='analyst@finance.dev', password='Analyst@1234',
    full_name='Bob Analyst', role=Role.ANALYST
)
viewer = User.objects.create_user(
    email='viewer@finance.dev', password='Viewer@1234',
    full_name='Carol Viewer', role=Role.VIEWER
)
print(f"  ✓ admin@finance.dev  (admin)")
print(f"  ✓ analyst@finance.dev  (analyst)")
print(f"  ✓ viewer@finance.dev  (viewer)")

# ── Records ───────────────────────────────────────────────────────────────────
print("Creating financial records...")
INCOME_DATA = [
    (Category.SALARY,    85000, 'Monthly salary'),
    (Category.FREELANCE, 12000, 'Freelance web project'),
    (Category.INVESTMENT, 3500, 'Dividend payout'),
]
EXPENSE_DATA = [
    (Category.RENT,          25000, 'Monthly rent'),
    (Category.FOOD,           4500, 'Groceries'),
    (Category.TRANSPORT,      2000, 'Metro + cab'),
    (Category.UTILITIES,      3200, 'Electricity & internet'),
    (Category.ENTERTAINMENT,  1800, 'OTT subscriptions'),
    (Category.HEALTHCARE,     5000, 'Doctor visit + meds'),
    (Category.EDUCATION,      8000, 'Online course'),
]

today = datetime.date.today()
records = []
for i in range(7):  # last 7 months
    month_date = today.replace(day=15) - datetime.timedelta(days=i * 30)
    for cat, base_amount, desc in INCOME_DATA:
        amount = round(base_amount + random.uniform(-500, 500), 2)
        records.append(FinancialRecord(
            created_by=admin, amount=amount,
            record_type=RecordType.INCOME, category=cat,
            date=month_date, description=f"{desc} — {month_date.strftime('%b %Y')}"
        ))
    for cat, base_amount, desc in EXPENSE_DATA:
        amount = round(base_amount + random.uniform(-200, 200), 2)
        records.append(FinancialRecord(
            created_by=admin, amount=amount,
            record_type=RecordType.EXPENSE, category=cat,
            date=month_date - datetime.timedelta(days=random.randint(0, 10)),
            description=f"{desc} — {month_date.strftime('%b %Y')}"
        ))

FinancialRecord.objects.bulk_create(records)
print(f"  ✓ {len(records)} records created")
print("\nDone! Start server: python manage.py runserver")
