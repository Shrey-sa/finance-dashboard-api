"""
Management command to seed the database with sample data for testing.
Usage: python manage.py seed_data
"""
import random
import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User, Role
from records.models import FinancialRecord, RecordType, Category


INCOME_CATEGORIES = [Category.SALARY, Category.FREELANCE, Category.INVESTMENT]
EXPENSE_CATEGORIES = [
    Category.FOOD, Category.TRANSPORT, Category.UTILITIES,
    Category.HEALTHCARE, Category.ENTERTAINMENT, Category.EDUCATION,
    Category.RENT, Category.OTHER
]


class Command(BaseCommand):
    help = 'Seeds database with sample users and financial records'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Create users
        users = {}
        specs = [
            ('admin@finance.dev', 'Admin User', Role.ADMIN, 'adminpass123'),
            ('analyst@finance.dev', 'Analyst User', Role.ANALYST, 'analystpass123'),
            ('viewer@finance.dev', 'Viewer User', Role.VIEWER, 'viewerpass123'),
        ]
        for email, name, role, pw in specs:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'full_name': name, 'role': role}
            )
            if created:
                user.set_password(pw)
                user.save()
                self.stdout.write(f'  Created {role}: {email} / {pw}')
            users[role] = user

        # Seed 60 records spread over last 6 months
        admin = users[Role.ADMIN]
        today = timezone.now().date()
        for i in range(60):
            days_ago = random.randint(0, 180)
            record_date = today - datetime.timedelta(days=days_ago)
            is_income = random.random() > 0.45
            if is_income:
                cat = random.choice(INCOME_CATEGORIES)
                amount = Decimal(str(round(random.uniform(5000, 150000), 2)))
            else:
                cat = random.choice(EXPENSE_CATEGORIES)
                amount = Decimal(str(round(random.uniform(100, 20000), 2)))

            FinancialRecord.objects.create(
                created_by=admin,
                amount=amount,
                record_type=RecordType.INCOME if is_income else RecordType.EXPENSE,
                category=cat,
                date=record_date,
                description=f'Auto-seeded record #{i+1}',
            )

        self.stdout.write(self.style.SUCCESS('Done. 60 records created.'))
        self.stdout.write('')
        self.stdout.write('Test credentials:')
        for email, _, role, pw in specs:
            self.stdout.write(f'  [{role:8}]  {email}  /  {pw}')
