from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.http import HttpResponseRedirect
from sslcommerz_lib import SSLCOMMERZ
from orders.views import OrderViewSet
from rest_framework.test import APIRequestFactory, force_authenticate
from datetime import date



@api_view(['POST'])
def initiate_payment(request):
    user = request.user
    amount = request.data.get("amount")
    cart_id = request.data.get("cartId")
    total_items = request.data.get("totalItems")
    if user.phone == None:
        user.phone = "01234567891"

    ssl_settings = {
        'store_id': 'pzafi6810e1dc1b643',
        'store_pass': 'pzafi6810e1dc1b643@ssl',
        'issandbox': True
    }

    sslcz = SSLCOMMERZ(ssl_settings)

    post_body = {
        'total_amount': amount,
        'currency': 'BDT',
        'tran_id': f"transectionId{cart_id}{date.today().strftime('%Y%m%d')}",
        'success_url': f"{settings.BACKEND_URL}/payment/api/success/",
        'fail_url': f"{settings.BACKEND_URL}/payment/api/fail/",
        'cancel_url': f"{settings.BACKEND_URL}/payment/api/cancel/",
        'emi_option': 0,
        'cus_name': f"{user.first_name} {user.last_name}",
        'cus_email': user.email,
        'cus_phone': user.phone,
        'cus_add1': "Somewhere",
        'cus_city': "From",
        'cus_country': "The Earth",
        'shipping_method': "NO",
        'multi_card_name': "",
        'num_of_item': total_items,
        'product_name': "Clothing & Lifestyle Products",
        'product_category': "General",
        'product_profile': "general"
    }

    response = sslcz.createSession(post_body)
    print(response)

    if response.get("status") == "SUCCESS":
        return Response({"payment_url": response["GatewayPageURL"]})

    return Response(
        {"error": "Payment initiation failed"},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def payment_success(request):
    user = request.user
    tran_id = request.data.get("tran_id")
    factory = APIRequestFactory()

    # Simulate a request to the checkout action
    checkout_request = factory.post('/orders/api/orders/checkout/', data={'tran_id': tran_id})
    force_authenticate(checkout_request, user=user)

    view = OrderViewSet.as_view({'post': 'checkout'})
    response = view(checkout_request)

    # If successful, redirect to frontend
    if response.status_code == 201:
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}/payment/success/")

    # Otherwise return error
    return Response(
        {"error": "Checkout failed after payment."},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def payment_cancel(request):
    return HttpResponseRedirect(f"{settings.FRONTEND_URL}/payment/cancel/")


@api_view(['POST'])
def payment_fail(request):
    return HttpResponseRedirect(f"{settings.FRONTEND_URL}/payment/fail/")

