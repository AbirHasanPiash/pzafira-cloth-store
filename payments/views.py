from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from cart.models import Cart
from django.http import HttpResponseRedirect
from sslcommerz_lib import SSLCOMMERZ
from orders.views import OrderViewSet
from rest_framework.test import APIRequestFactory, force_authenticate
from datetime import date
from django.http import JsonResponse
from .models import TemporaryAddress


def extract_cart_id_from_tran_id(tran_id):
    try:
        return int(tran_id.replace("transectionId", "")[:-8])
    except:
        return None


@api_view(['POST'])
def initiate_payment(request):
    user = request.user
    amount = request.data.get("amount")
    cart_id = request.data.get("cartId")
    total_items = request.data.get("totalItems")
    address = request.data.get("address")
    city = request.data.get("city")
    country = request.data.get("country")
    unique_id = f"{cart_id}{date.today().strftime('%Y%m%d')}"

    TemporaryAddress.objects.update_or_create(
        user=user,
        cart_id=cart_id,
        unique_id=unique_id,
        defaults={
            'address': address,
            'city': city,
            'country': country
        }
    )

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
        'cus_add1': address,
        'cus_city': city,
        'cus_country': country,
        'shipping_method': "NO",
        'multi_card_name': "",
        'num_of_item': total_items,
        'product_name': "Clothing & Lifestyle Products",
        'product_category': "General",
        'product_profile': "general"
    }

    response = sslcz.createSession(post_body)

    if response.get("status") == "SUCCESS":
        return Response({"payment_url": response["GatewayPageURL"]})

    return Response(
        {"error": "Payment initiation failed"},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def payment_success(request):
    tran_id = request.data.get("tran_id")  # get transaction ID from SSLCOMMERZ

    # Extract cart_id from tran_id
    cart_id = extract_cart_id_from_tran_id(tran_id)
    cart = Cart.objects.select_related('user').filter(id=cart_id).first()


    if not cart:
        return Response({"error": "Cart not found for transaction."}, status=400)

    user = cart.user

    unique_id = f"{cart_id}{date.today().strftime('%Y%m%d')}"
    temp_address = TemporaryAddress.objects.filter(unique_id=unique_id).first()
    if not temp_address:
        return Response({"error": "Address not found for this transaction."}, status=400)

    address = temp_address.address
    city = temp_address.city
    country = temp_address.country
    full_address = f"{address}, {city}, {country}"
    temp_address.delete()


    # Simulate a request to the checkout action
    factory = APIRequestFactory()
    checkout_request = factory.post(
        '/orders/api/orders/checkout/',
        {"tran_id": tran_id,
         "address": full_address},
        format='json'
    )
    force_authenticate(checkout_request, user=user)

    view = OrderViewSet.as_view({'post': 'checkout'})
    response = view(checkout_request)

    if response.status_code == 201:
        return HttpResponseRedirect(f"{settings.FRONTEND_URL}/payment/success/")
    
    return JsonResponse({"error": "Checkout failed after payment."}, status=400)


@api_view(['POST'])
def payment_cancel(request):
    return HttpResponseRedirect(f"{settings.FRONTEND_URL}/payment/cancel/")


@api_view(['POST'])
def payment_fail(request):
    return HttpResponseRedirect(f"{settings.FRONTEND_URL}/payment/fail/")

