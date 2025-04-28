from django.db import models
from django.conf import settings
from products.models import ProductVariant

class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Wishlist"

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']
        unique_together = ('wishlist', 'variant')

    def __str__(self):
        return f"{self.variant} in {self.wishlist}"