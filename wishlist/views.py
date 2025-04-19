from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Wishlist, WishlistItem
from .serializers import WishlistItemSerializer
from products.models import ProductVariant

class WishlistItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing wishlist items of the authenticated user.

    Key Features:
    - Allows users to add product variants to their wishlist.
    - Users can view all items in their wishlist.
    - Users can remove items from their wishlist.
    - Ensures that duplicate wishlist items are not added.
    - Only the owner of a wishlist can modify or delete its items.
    """
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return WishlistItem.objects.none()
        return WishlistItem.objects.filter(wishlist__user=self.request.user)

    def create(self, request, *args, **kwargs):
        variant_id = request.data.get('variant_id')
        if not variant_id:
            return Response({'error': 'Variant ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            variant = ProductVariant.objects.get(id=variant_id)
        except ProductVariant.DoesNotExist:
            return Response({'error': 'Product variant not found.'}, status=status.HTTP_404_NOT_FOUND)

        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        item, created = WishlistItem.objects.get_or_create(wishlist=wishlist, variant=variant)

        if not created:
            return Response({'message': 'Already in wishlist.'}, status=status.HTTP_200_OK)

        return Response(WishlistItemSerializer(item).data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.wishlist.user != request.user:
            return Response({'error': 'Not allowed to delete this item.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)