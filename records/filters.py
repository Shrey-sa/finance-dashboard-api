import django_filters
from .models import FinancialRecord


class FinancialRecordFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(field_name='date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='date', lookup_expr='lte')
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')

    class Meta:
        model = FinancialRecord
        fields = ['record_type', 'category', 'date_from', 'date_to', 'amount_min', 'amount_max']
