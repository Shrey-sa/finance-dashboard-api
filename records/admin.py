from django.contrib import admin
from .models import FinancialRecord


@admin.register(FinancialRecord)
class FinancialRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'amount', 'record_type', 'category', 'date', 'created_by', 'is_deleted')
    list_filter = ('record_type', 'category', 'is_deleted')
    search_fields = ('description',)
    date_hierarchy = 'date'
