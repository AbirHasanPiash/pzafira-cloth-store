from rest_framework import serializers
from products.serializers import ProductVariantSerializer
from products.models import ProductVariant
from .models import CartItem, Cart




class CartItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    variant_detail = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.select_related('product', 'color', 'size'),
        source='variant',
        write_only=True,
        required=False
    )
    quantity = serializers.IntegerField(required=True, min_value=1)

    class Meta:
        model = CartItem
        fields = ['id', 'variant', 'variant_detail', 'quantity']

    def validate(self, attrs):
        variant = attrs.get('variant')
        quantity = attrs.get('quantity')

        if quantity <= 0:
            raise serializers.ValidationError(
                {"quantity": "You must add at least 1 item."}
            )

        if variant.stock < quantity:
            raise serializers.ValidationError(
                {"quantity": f"Only {variant.stock} items available in stock."}
            )

        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items']
        read_only_fields = ['user', 'created_at', 'items']
