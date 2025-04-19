from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from reviews.models import Review

from .models import (
    Category, Brand, Product, ProductImage, Color, Size, ProductVariant
)
from .serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer,
    ProductCreateUpdateSerializer, DetailProductSerializer,
    ProductImageSerializer, ProductVariantCreateSerializer,
    ColorSerializer, SizeSerializer
)
from .permissions import IsAdminOrReadOnly
from .filters import ProductFilter


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing product categories.

    Allows admin users to create, update, and delete categories.
    Read-only access (list and retrieve) is available to all users.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class BrandViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing product brands.

    Allows admin users to create, update, and delete brand entries.
    All users can view the list of brands and retrieve individual brand details.
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]


class ColorViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing available product colors.

    Admin users can perform full CRUD operations on color entries.
    Read-only access is available to all users.
    """
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAdminOrReadOnly]


class SizeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing available product sizes.

    Admin users have full access to create, update, and delete sizes.
    All users can view size options for product filtering and selection.
    """
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [IsAdminOrReadOnly]



class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing products in the store.

    Admin users can perform full CRUD operations on products.
    Regular users can view only active products with search, filtering, and ordering support.
    """
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at']

    def get_queryset(self):

        queryset = Product.objects.all()

        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)

        return queryset.select_related('category', 'brand').prefetch_related(
            'images'
        )

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer



class DetailProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for retrieving detailed product information.

    Provides comprehensive data including variants, images, and reviews.
    Admin users can manage product records, while all users can view detailed information for active products.
    Supports search, filtering, and ordering.
    """
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'average_rating']
    filterset_class = ProductFilter

    def get_queryset(self):
        variant_qs = ProductVariant.objects.select_related('color', 'size')
        review_qs = Review.objects.select_related('user')

        queryset = Product.objects.all()

        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)

        return queryset.select_related('category', 'brand').prefetch_related(
            'images',
            Prefetch('variants', queryset=variant_qs),
            Prefetch('reviews', queryset=review_qs)
        )

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return DetailProductSerializer



class ProductImageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing images associated with a specific product.

    Allows admin users to upload, update, and delete product images.
    Supports multipart/form-data for image uploads and ensures only one primary image per product.
    """
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ProductImage.objects.none()
        return ProductImage.objects.filter(product_id=self.kwargs['detail_product_pk'])

    def perform_create(self, serializer):
        if getattr(self, 'swagger_fake_view', False):
            return
        product = Product.objects.get(pk=self.kwargs['detail_product_pk'])
        serializer.save(product=product)

    def perform_update(self, serializer):
        if getattr(self, 'swagger_fake_view', False):
            return
        product = Product.objects.get(pk=self.kwargs['detail_product_pk'])
        if self.request.data.get('is_primary') == 'true':
            ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
        serializer.save(product=product)


class ProductVariantViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing product variants tied to a specific product.

    Allows admin users to create, update, and delete variants for a given product.
    Retrieves variants based on the parent product ID and ensures association during create and update operations.
    """

    serializer_class = ProductVariantCreateSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return
        return ProductVariant.objects.filter(product_id=self.kwargs['detail_product_pk'])

    def perform_create(self, serializer):
        if getattr(self, 'swagger_fake_view', False):
            return
        product = get_object_or_404(Product, pk=self.kwargs['detail_product_pk'])
        serializer.save(product=product)

    def perform_update(self, serializer):
        if getattr(self, 'swagger_fake_view', False):
            return
        product = get_object_or_404(Product, pk=self.kwargs['detail_product_pk'])
        serializer.save(product=product)