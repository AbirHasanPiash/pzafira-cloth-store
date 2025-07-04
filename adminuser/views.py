from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.utils.timezone import now, timedelta
from django.db.models import Count, Sum, DecimalField
from decimal import Decimal
from users.models import User
from orders.models import Order
from products.models import Product
from .serializers import TopProductSerializer, TopUserSerializer
from django.db.models.functions import Coalesce, TruncDay, TruncMonth

class AdminDashboardView(APIView):

    """
    API endpoint for retrieving summarized statistics for the admin dashboard.

    This endpoint is accessible only to admin users and provides the following data:
    
    - **Weekly Orders:** Total number of orders placed in the last 7 days.
    - **Monthly Orders:** Total number of orders placed in the last 30 days.
    - **Top Liked Products:** Top 5 products with the highest number of user reviews.
    - **Top Users:** Top 5 users based on the total quantity of products purchased.
    - **Sales This Month:** Total revenue generated from orders created in the current month.
    - **Sales Last Month:** Total revenue generated from orders in the previous month.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        today = now()
        last_week = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)

        # Orders
        weekly_orders_count = Order.objects.filter(created_at__gte=last_week).count()
        monthly_orders_count = Order.objects.filter(created_at__gte=last_30_days).count()

        # Top 5 liked products (based on number of reviews)
        top_liked_products = Product.objects.annotate(
            total_reviews=Count('reviews')
        ).order_by('-average_rating')[:5]

        # Top 5 users by total quantity purchased
        top_users = User.objects.annotate(
            total_purchased=Coalesce(Sum('orders__total_price'), Decimal(0.00), output_field=DecimalField(max_digits=10, decimal_places=2))
        ).order_by('-total_purchased')[:5]

        # Monthly sales (this and previous month)
        this_month = today.replace(day=1)
        last_month = (this_month - timedelta(days=1)).replace(day=1)

        sales_this_month = Order.objects.filter(created_at__gte=this_month).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        sales_last_month = Order.objects.filter(
            created_at__gte=last_month,
            created_at__lt=this_month
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        return Response({
            "weekly_orders": weekly_orders_count,
            "monthly_orders": monthly_orders_count,
            "top_liked_products": TopProductSerializer(top_liked_products, many=True).data,
            "top_users": TopUserSerializer(top_users, many=True).data,
            "sales_this_month": sales_this_month,
            "sales_last_month": sales_last_month,
        })
    

# ✅ 1. Daily Orders - Current Month
class DailyOrdersCurrentMonth(APIView):
    def get(self, request):
        start = now().replace(day=1)
        orders = (
            Order.objects.filter(created_at__date__gte=start, payment_status='paid')
            .annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        return Response(orders)

# ✅ 2. Monthly Orders - Last 12 Months
class MonthlyOrdersLast12(APIView):
    def get(self, request):
        start = now() - timedelta(days=365)
        orders = (
            Order.objects.filter(created_at__date__gte=start, payment_status='paid')
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        return Response(orders)

# ✅ 3. Daily Sales - Current Month
class DailySalesCurrentMonth(APIView):
    def get(self, request):
        start = now().replace(day=1)
        sales = (
            Order.objects.filter(created_at__date__gte=start, payment_status='paid')
            .annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(total_sales=Sum('total_price'))
            .order_by('day')
        )
        return Response(sales)

# ✅ 4. Monthly Sales - Last 12 Months
class MonthlySalesLast12(APIView):
    def get(self, request):
        start = now() - timedelta(days=365)
        sales = (
            Order.objects.filter(created_at__date__gte=start, payment_status='paid')
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(total_sales=Sum('total_price'))
            .order_by('month')
        )
        return Response(sales)