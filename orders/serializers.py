from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductVariantSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'variant', 'quantity', 'price']
        read_only_fields = ['id', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    tran_id = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'status',
            'status_display',
            'payment_status',
            'payment_status_display',
            'total_price',
            'created_at',
            'updated_at',
            'items',
            'tran_id',
        ]
        read_only_fields = [
            'id',
            'total_price',
            'created_at',
            'updated_at',
            'items',
            # 'payment_status',
            'tran_id',
        ]
