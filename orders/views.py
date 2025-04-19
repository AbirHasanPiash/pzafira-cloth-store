from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from django.db import transaction
from cart.models import Cart, CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .permissions import IsAdminOrReadOnlyOrder
from products.models import ProductVariant

class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing customer orders.

    - Allows authenticated users to:
      • View their own orders.
    
    - Allows admin users to:
      • View all orders.
      • Update or delete any order.

    - Restrictions:
      • Direct order creation via this endpoint is disabled.
      • Only admin users can modify or delete orders after checkout.

    - Checkout action:
      • Creates an order from the user's cart.
      • Validates stock availability for each item.
      • Deducts purchased quantities from product variant stock.
      • Saves order items and calculates total price.
      • Clears the user's cart after successful order placement.
    """

    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnlyOrder]
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.select_related('user').prefetch_related(
            'items__variant__product',
            'items__variant__color',
            'items__variant__size'
        )
        if getattr(self, 'swagger_fake_view', False):
            return queryset.none()
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(user=self.request.user)


    def create(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Use the checkout endpoint to create orders.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise permissions.PermissionDenied("You are not allowed to update an order after checkout.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise permissions.PermissionDenied("You are not allowed to update an order after checkout.")
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise permissions.PermissionDenied("Only admins can delete orders.")
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    @transaction.atomic
    def checkout(self, request):
        user = request.user

        # Get the user's cart
        cart = Cart.objects.select_related('user').filter(user=user).first()
        if not cart:
            return Response({'error': 'Cart not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Load cart items with related variant data
        items = CartItem.objects.select_related(
            'variant', 'variant__color', 'variant__size', 'variant__product'
        ).filter(cart=cart)

        if not items.exists():
            return Response({'error': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create order
        order = Order.objects.create(user=user, total_price=0)
        total_price = 0
        order_items = []
        updated_variants = []

        # Process cart items and create order items
        for item in items:
            variant = item.variant

            if item.quantity > variant.stock:
                return Response({
                    'error': f"Not enough stock for {variant}. Available: {variant.stock}"
                }, status=status.HTTP_400_BAD_REQUEST)

            order_items.append(OrderItem(
                order=order,
                variant=variant,
                quantity=item.quantity,
                price=variant.price
            ))

            variant.stock -= item.quantity
            updated_variants.append(variant)
            total_price += variant.price * item.quantity

        OrderItem.objects.bulk_create(order_items)
        ProductVariant.objects.bulk_update(updated_variants, ['stock'])

        # Finalize order
        order.total_price = total_price
        order.save()

        # Clear cart
        items.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
