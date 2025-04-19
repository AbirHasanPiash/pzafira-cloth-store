from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import Order
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    if created:
        transaction.on_commit(lambda: _send_email(instance))


def _send_email(order):
    try:
        order = Order.objects.prefetch_related(
            'items__variant__size',
            'items__variant__color',
            'items__variant__product'
        ).select_related('user').get(pk=order.pk)
        
        subject = f"Order #{order.id} Confirmation"
        message = render_to_string('orders/order_confirmation_email.html', {
            'user': order.user,
            'order': order,
            'order_items': order.items.all()
        })

        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            html_message=message,
            fail_silently=False
        )
    except Exception as e:
        logger.error(f"Failed to send order confirmation email for Order #{order.pk}: {e}")
