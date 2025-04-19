from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg
from .models import Review

@receiver([post_save, post_delete], sender=Review)
def update_average_rating(sender, instance, **kwargs):
    product = instance.product
    average = product.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    product.average_rating = round(average, 2)
    product.save(update_fields=['average_rating'])
