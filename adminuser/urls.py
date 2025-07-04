from django.urls import path
from .views import AdminDashboardView
from .views import (
    DailyOrdersCurrentMonth, MonthlyOrdersLast12,
    DailySalesCurrentMonth, MonthlySalesLast12
)

urlpatterns = [
    path('admin-dashboard/', AdminDashboardView.as_view(), name='admin-dashboard'),
    path('daily-orders/', DailyOrdersCurrentMonth.as_view()),
    path('monthly-orders/', MonthlyOrdersLast12.as_view()),
    path('daily-sales/', DailySalesCurrentMonth.as_view()),
    path('monthly-sales/', MonthlySalesLast12.as_view()),
]
