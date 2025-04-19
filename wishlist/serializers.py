from rest_framework import serializers
from .models import WishlistItem
from products.serializers import ProductVariantSerializer

class WishlistItemSerializer(serializers.ModelSerializer):
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = WishlistItem
        fields = ['id', 'variant', 'variant_id']