"""
Dashboard analytics service.
Aggregation logic is isolated here to keep views thin.
"""
from decimal import Decimal
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncWeek
from django.utils import timezone
import datetime

from .models import FinancialRecord, RecordType


def _active_records():
    return FinancialRecord.objects.filter(is_deleted=False)


def get_summary():
    """Total income, expenses, net balance."""
    qs = _active_records()
    totals = qs.aggregate(
        total_income=Sum('amount', filter=Q(record_type=RecordType.INCOME)),
        total_expense=Sum('amount', filter=Q(record_type=RecordType.EXPENSE)),
    )
    income = totals['total_income'] or Decimal('0')
    expense = totals['total_expense'] or Decimal('0')
    return {
        'total_income': income,
        'total_expense': expense,
        'net_balance': income - expense,
        'total_records': qs.count(),
    }


def get_category_totals():
    """Breakdown by category."""
    qs = (
        _active_records()
        .values('category', 'record_type')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('category', 'record_type')
    )
    return list(qs)


def get_monthly_trends(months=6):
    """Last N months of income vs expense."""
    since = timezone.now().date() - datetime.timedelta(days=months * 30)
    qs = (
        _active_records()
        .filter(date__gte=since)
        .annotate(month=TruncMonth('date'))
        .values('month', 'record_type')
        .annotate(total=Sum('amount'))
        .order_by('month', 'record_type')
    )
    return list(qs)


def get_weekly_trends(weeks=8):
    """Last N weeks of income vs expense."""
    since = timezone.now().date() - datetime.timedelta(weeks=weeks)
    qs = (
        _active_records()
        .filter(date__gte=since)
        .annotate(week=TruncWeek('date'))
        .values('week', 'record_type')
        .annotate(total=Sum('amount'))
        .order_by('week', 'record_type')
    )
    return list(qs)


def get_recent_activity(limit=10):
    """Most recent N records."""
    return _active_records().select_related('created_by').order_by('-date', '-created_at')[:limit]
