import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='variants__price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='variants__price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['category', 'brand', 'target_audience', 'variants__size', 'variants__color']