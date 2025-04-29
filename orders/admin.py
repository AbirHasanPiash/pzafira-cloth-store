from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'payment_status', 'tran_id', 'created_at']
    search_fields = ['id', 'user__email', 'tran_id']
    list_filter = ['status', 'payment_status', 'created_at']
