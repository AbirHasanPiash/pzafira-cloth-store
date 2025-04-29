from rest_framework import serializers
from products.serializers import ProductVariantSerializer
from products.models import ProductVariant
from .models import CartItem, Cart




class CartItemSerializer(serializers.ModelSerializer):
    cart = serializers.PrimaryKeyRelatedField(read_only=True)
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
        fields = ['id', 'cart', 'variant', 'variant_detail', 'quantity']

    def validate(self, attrs):
        quantity = attrs.get('quantity')
        if quantity is None:
            raise serializers.ValidationError(
                {"quantity": "This field is required."}
            )

        # If creating (no instance), variant must come from attrs
        if self.instance is None:
            variant = attrs.get('variant')
            if variant is None:
                raise serializers.ValidationError(
                    {"variant_detail": "This field is required for creating a cart item."}
                )
        else:
            # Updating: get variant from existing instance
            variant = self.instance.variant

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
