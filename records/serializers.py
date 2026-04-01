from rest_framework import serializers
from .models import FinancialRecord, RecordType, Category


class FinancialRecordSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)

    class Meta:
        model = FinancialRecord
        fields = (
            'id', 'amount', 'record_type', 'category', 'date',
            'description', 'created_by_email', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_by_email', 'created_at', 'updated_at')

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be a positive number.')
        return value

    def validate_record_type(self, value):
        if value not in RecordType.values:
            raise serializers.ValidationError(f'Must be one of: {RecordType.values}')
        return value

    def validate_category(self, value):
        if value not in Category.values:
            raise serializers.ValidationError(f'Must be one of: {Category.values}')
        return value


class RecordListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views."""
    class Meta:
        model = FinancialRecord
        fields = ('id', 'amount', 'record_type', 'category', 'date', 'description')
