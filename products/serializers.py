from rest_framework import serializers
from .models import Category, Brand, Product, ProductImage, Color, Size, ProductVariant
from reviews.serializers import ReviewSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class BrandSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Brand
        fields = ['id', 'name', 'logo']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name']


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name']


class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'uploaded_at']
        read_only_fields = ['uploaded_at']
        extra_kwargs = {
            'image': {'required': False},
        }



class ProductSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source='brand.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'brand',
             'images', 'is_active', 'created_at'
        ]


class ProductVariantSerializer(serializers.ModelSerializer):
    product = serializers.CharField(source='product.name')
    product_id = serializers.IntegerField(source='product.id')
    color = serializers.CharField(source='color.name')
    size = serializers.CharField(source='size.name')

    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'product_id', 'color', 'size', 'stock', 'price']


class DetailProductSerializer(serializers.ModelSerializer):
    brand = serializers.CharField(source='brand.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'brand', 'images',
            'variants', 'reviews', 'average_rating', 'is_active', 'created_at'
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'category', 'brand', 'is_active']


class ProductVariantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'color', 'size', 'stock', 'price']
