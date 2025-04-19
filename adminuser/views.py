from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.utils.timezone import now, timedelta
from django.db.models import Count, Avg, Sum
from users.models import User
from orders.models import Order
from products.models import Product
from .serializers import TopProductSerializer, TopUserSerializer  # Adjust if location differs

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
        ).order_by('-total_reviews')[:5]

        # Top 5 users by total quantity purchased
        top_users = User.objects.annotate(
            total_purchased=Sum('orders__items__quantity')
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