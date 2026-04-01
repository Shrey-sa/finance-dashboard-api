from django.db import models
from django.conf import settings
from django.utils import timezone


class RecordType(models.TextChoices):
    INCOME = 'income', 'Income'
    EXPENSE = 'expense', 'Expense'


class Category(models.TextChoices):
    SALARY = 'salary', 'Salary'
    FREELANCE = 'freelance', 'Freelance'
    INVESTMENT = 'investment', 'Investment'
    FOOD = 'food', 'Food'
    TRANSPORT = 'transport', 'Transport'
    UTILITIES = 'utilities', 'Utilities'
    HEALTHCARE = 'healthcare', 'Healthcare'
    ENTERTAINMENT = 'entertainment', 'Entertainment'
    EDUCATION = 'education', 'Education'
    RENT = 'rent', 'Rent'
    OTHER = 'other', 'Other'


class FinancialRecord(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='records'
    )
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    record_type = models.CharField(max_length=10, choices=RecordType.choices)
    category = models.CharField(max_length=30, choices=Category.choices, default=Category.OTHER)
    date = models.DateField()
    description = models.TextField(blank=True, default='')
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['record_type']),
            models.Index(fields=['category']),
            models.Index(fields=['date']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        return f'{self.record_type.upper()} | {self.amount} | {self.date}'

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
