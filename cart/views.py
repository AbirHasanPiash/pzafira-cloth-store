from rest_framework import viewsets, permissions, serializers, status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing the authenticated user's cart.

    - Authenticated users can view their own cart.
    - Admins can view all user carts.
    - No updates or deletions are allowed through this view.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Returns the carts for the authenticated user.
        Admins can view all carts.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        user = self.request.user
        if user.is_staff:
            return Cart.objects.all()
        return Cart.objects.filter(user=user)

    def get_object(self):
        """
        Retrieves the authenticated user's cart.
        """
        return get_object_or_404(Cart, user=self.request.user)

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_cart(self, request):
        """
        Clears all items from the authenticated user's cart.
        """
        cart = get_object_or_404(Cart, user=request.user)
        cart.items.all().delete()
        return Response({"detail": "Cart cleared successfully."}, status=status.HTTP_204_NO_CONTENT)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing items in the user's cart.

    - Users can only access their own cart items.
    - Admins can view all carts but not cart items of other users.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Users can only see their own cart items.
        Admins can see only their own cart items too (for security).
        """
        queryset = CartItem.objects.select_related(
            'cart', 'variant', 'variant__product', 'variant__color', 'variant__size'
        )
        if getattr(self, 'swagger_fake_view', False):
            return Cart.objects.none()
        return queryset.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        variant = serializer.validated_data['variant']
        quantity = serializer.validated_data['quantity']
        image = serializer.validated_data.get('image')

        existing_item = CartItem.objects.filter(cart=cart, variant=variant).first()

        if existing_item:
            new_quantity = existing_item.quantity + quantity
            if new_quantity > variant.stock:
                raise serializers.ValidationError(
                    f"Only {variant.stock} items available. You already have {existing_item.quantity}."
                )
            existing_item.quantity = new_quantity
            existing_item.save()
        else:
            if quantity > variant.stock:
                raise serializers.ValidationError(
                    f"Only {variant.stock} items available."
                )
            serializer.save(cart=cart, image=image)


    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.cart.user != self.request.user:
            raise permissions.PermissionDenied('You do not have permission to edit this cart item.')

        new_variant = serializer.validated_data.get('variant', instance.variant)
        new_quantity = serializer.validated_data.get('quantity', instance.quantity)

        if new_quantity > new_variant.stock:
            raise serializers.ValidationError({'quantity': 'Requested quantity exceeds available stock.'})

        image = serializer.validated_data.get('image', instance.image)
        serializer.save(image=image)

    def perform_destroy(self, instance):
        if instance.cart.user != self.request.user:
            raise permissions.PermissionDenied('You do not have permission to delete this cart item.')
        instance.delete()

