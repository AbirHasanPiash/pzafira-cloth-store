from django.urls import path
from . import views

urlpatterns = [
    path('initiate/', views.initiate_payment, name='initiate-payment'),
    path('success/', views.payment_success, name='payment-success'),
    path('cancel/', views.payment_cancel, name='payment-cancel'),
    path('fail/', views.payment_fail, name='payment-fail'),
]
