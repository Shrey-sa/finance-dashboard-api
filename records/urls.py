from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FinancialRecordViewSet,
    DashboardSummaryView,
    CategoryTotalsView,
    MonthlyTrendsView,
    WeeklyTrendsView,
    RecentActivityView,
)

router = DefaultRouter()
router.register('records', FinancialRecordViewSet, basename='records')

urlpatterns = [
    path('', include(router.urls)),
    # Dashboard
    path('dashboard/summary/', DashboardSummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/categories/', CategoryTotalsView.as_view(), name='dashboard-categories'),
    path('dashboard/trends/monthly/', MonthlyTrendsView.as_view(), name='dashboard-monthly'),
    path('dashboard/trends/weekly/', WeeklyTrendsView.as_view(), name='dashboard-weekly'),
    path('dashboard/recent/', RecentActivityView.as_view(), name='dashboard-recent'),
]
