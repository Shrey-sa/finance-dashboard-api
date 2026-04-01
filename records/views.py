from decimal import Decimal
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.permissions import IsAdmin, IsAnalystOrAdmin, IsActiveUser
from .filters import FinancialRecordFilter
from .models import FinancialRecord
from .serializers import FinancialRecordSerializer, RecordListSerializer
from . import services


class FinancialRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD for financial records with role-based access control:
      - All authenticated active users: list, retrieve
      - Analyst + Admin: access dashboard summaries
      - Admin only: create, update, destroy
    """
    filterset_class = FinancialRecordFilter
    search_fields = ['description', 'category']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        return FinancialRecord.objects.filter(is_deleted=False).select_related('created_by')

    def get_serializer_class(self):
        if self.action == 'list':
            return RecordListSerializer
        return FinancialRecordSerializer

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy', 'restore'):
            return [IsAuthenticated(), IsActiveUser(), IsAdmin()]
        return [IsAuthenticated(), IsActiveUser()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        """Soft delete instead of hard delete."""
        record = self.get_object()
        record.soft_delete()
        return Response(
            {'success': True, 'message': 'Record soft-deleted.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsActiveUser, IsAdmin])
    def restore(self, request, pk=None):
        """Restore a soft-deleted record."""
        try:
            record = FinancialRecord.objects.get(pk=pk, is_deleted=True)
        except FinancialRecord.DoesNotExist:
            return Response(
                {'success': False, 'errors': 'No deleted record found with this ID.'},
                status=status.HTTP_404_NOT_FOUND
            )
        record.is_deleted = False
        record.deleted_at = None
        record.save()
        return Response({'success': True, 'record': FinancialRecordSerializer(record).data})

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated, IsActiveUser, IsAdmin],
            url_path='deleted')
    def deleted_records(self, request):
        """List soft-deleted records (admin only)."""
        qs = FinancialRecord.objects.filter(is_deleted=True)
        serializer = RecordListSerializer(qs, many=True)
        return Response({'success': True, 'records': serializer.data})


class DashboardSummaryView(generics.GenericAPIView):
    """
    Overall summary: income, expense, net balance.
    Access: Analyst + Admin
    """
    permission_classes = [IsAuthenticated, IsActiveUser, IsAnalystOrAdmin]

    def get(self, request):
        data = services.get_summary()
        return Response({'success': True, 'summary': {k: str(v) if isinstance(v, Decimal) else v for k, v in data.items()}})


class CategoryTotalsView(generics.GenericAPIView):
    """
    Totals grouped by category and type.
    Access: Analyst + Admin
    """
    permission_classes = [IsAuthenticated, IsActiveUser, IsAnalystOrAdmin]

    def get(self, request):
        data = services.get_category_totals()
        # Serialize Decimals
        result = [
            {**row, 'total': str(row['total'])}
            for row in data
        ]
        return Response({'success': True, 'category_totals': result})


class MonthlyTrendsView(generics.GenericAPIView):
    """
    Monthly income vs expense trends.
    Access: Analyst + Admin
    """
    permission_classes = [IsAuthenticated, IsActiveUser, IsAnalystOrAdmin]

    def get(self, request):
        months = int(request.query_params.get('months', 6))
        months = max(1, min(months, 24))  # clamp between 1-24
        data = services.get_monthly_trends(months)
        result = [
            {**row, 'month': row['month'].strftime('%Y-%m'), 'total': str(row['total'])}
            for row in data
        ]
        return Response({'success': True, 'monthly_trends': result})


class WeeklyTrendsView(generics.GenericAPIView):
    """
    Weekly income vs expense trends.
    Access: Analyst + Admin
    """
    permission_classes = [IsAuthenticated, IsActiveUser, IsAnalystOrAdmin]

    def get(self, request):
        weeks = int(request.query_params.get('weeks', 8))
        weeks = max(1, min(weeks, 52))
        data = services.get_weekly_trends(weeks)
        result = [
            {**row, 'week': row['week'].strftime('%Y-%m-%d'), 'total': str(row['total'])}
            for row in data
        ]
        return Response({'success': True, 'weekly_trends': result})


class RecentActivityView(generics.GenericAPIView):
    """
    Recent financial activity.
    Access: All authenticated active users
    """
    permission_classes = [IsAuthenticated, IsActiveUser]

    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        limit = max(1, min(limit, 50))
        records = services.get_recent_activity(limit)
        serializer = FinancialRecordSerializer(records, many=True)
        return Response({'success': True, 'recent_activity': serializer.data})
