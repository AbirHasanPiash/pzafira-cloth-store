from rest_framework import viewsets, permissions, serializers
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing the authenticated user's cart.
    Only supports list and retrieve actions.
    Admins can view all carts.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Cart.objects.all()
        return Cart.objects.filter(user=user)

    def get_object(self):
        return get_object_or_404(Cart, user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing items in the user's cart.

    - Add items to the cart
    - Update quantity of items
    - Remove items from the cart

    Access restricted to cart owners and admins.
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CartItem.objects.select_related(
            'cart', 'variant', 'variant__product', 'variant__color', 'variant__size'
        )
        if self.request.user.is_staff:
            return queryset
        return queryset.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        variant = serializer.validated_data['variant']
        quantity = serializer.validated_data['quantity']

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
            serializer.save(cart=cart)

    def perform_update(self, serializer):
        instance = serializer.instance

        if instance.cart.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied('You do not have permission to edit this cart item.')

        new_variant = serializer.validated_data.get('variant', instance.variant)

        if new_variant != instance.variant:
            existing_item = CartItem.objects.filter(
                cart=instance.cart,
                variant=new_variant
            ).exclude(id=instance.id).first()

            if existing_item:
                cart, _ = Cart.objects.get_or_create(user=self.request.user)
                quantity = serializer.validated_data.get('quantity')
                if quantity <= existing_item.stock:
                    item = CartItem.objects.get_or_create(cart=cart, variant=existing_item)
                    item.save()
                    
        new_quantity = serializer.validated_data.get('quantity', instance.quantity)
        if new_quantity > new_variant.stock:
            raise serializers.ValidationError({'quantity': 'Requested quantity exceeds available stock.'})

        serializer.save()


    def perform_destroy(self, instance):
        if instance.cart.user != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied('You do not have permission to delete this cart item.')
        instance.delete()
