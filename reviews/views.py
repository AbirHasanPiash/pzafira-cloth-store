from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError
from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsOwnerOrAdmin


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing product reviews.

    - Allows authenticated users to:
      • Create a review for a specific product (one review per product).
      • Update or delete their own reviews.

    - Allows all users to:
      • View reviews for a specific product.

    - Restrictions:
      • A user can only leave one review per product.
      • Attempting to review the same product again will raise a validation error.
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return
        return Review.objects.filter(product_id=self.kwargs['detail_product_pk'])

    def perform_create(self, serializer):
        if getattr(self, 'swagger_fake_view', False):
            return
        product_id = self.kwargs['detail_product_pk']
        user = self.request.user

        if Review.objects.filter(user=user, product_id=product_id).exists():
            raise ValidationError("You have already reviewed this product. You can update your review instead.")

        serializer.save(user=user, product_id=product_id)