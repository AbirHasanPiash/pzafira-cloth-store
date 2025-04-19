from django.urls import path, include
from rest_framework_nested import routers
from reviews.views import ReviewViewSet
from .views import (
    CategoryViewSet, BrandViewSet, ProductViewSet, ProductImageViewSet,
    ColorViewSet, SizeViewSet, ProductVariantViewSet, DetailProductViewSet
)

# Main router
router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'colors', ColorViewSet, basename='color')
router.register(r'sizes', SizeViewSet, basename='size')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'detail-products', DetailProductViewSet, basename='detail_product')

# Nested router for product
detail_products_router = routers.NestedDefaultRouter(router, r'detail-products', lookup='detail_product')
detail_products_router.register(r'images', ProductImageViewSet, basename='product-images')
detail_products_router.register(r'variants', ProductVariantViewSet, basename='product-variants')
detail_products_router.register(r'reviews', ReviewViewSet, basename='product-reviews')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(detail_products_router.urls)),
]
