from django.shortcuts import get_object_or_404
from django.conf import settings
import stripe
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from sales.models import Payment, Invoice, SalesOrder
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sales.tasks import generate_invoice
import json
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    """Handles Stripe webhook events by fetching metadata from Stripe"""

    print("\n=== STRIPE WEBHOOK RECEIVED ===")

    try:
        payload = request.body.decode("utf-8")
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return JsonResponse({"error": "Webhook processing error"}, status=400)

    event_type = event.get("type")
    event_data = event["data"]["object"]
    print(f"EVENT TYPE: {event_type}")

    payment_intent_id = event_data.get("payment_intent")

    # 🔥 Always fetch metadata from PaymentIntent
    if payment_intent_id:
        try:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            sales_order_id = payment_intent.metadata.get("sales_order_id")
            print(f"✅ SALES ORDER ID: {sales_order_id}")
        except Exception as e:
            print(f"ERROR RETRIEVING PAYMENT INTENT: {str(e)}")
            return JsonResponse({"error": "Could not retrieve PaymentIntent metadata"}, status=500)
    else:
        sales_order_id = event_data.get("metadata", {}).get("sales_order_id")

    if not sales_order_id:
        print("ERROR: Missing sales_order_id")
        return JsonResponse({"error": "Missing sales_order_id"}, status=400)

    try:
        payment = get_object_or_404(Payment, sales_order__id=sales_order_id)
        sales_order = payment.sales_order

        payment.status = "succeeded"
        payment.save()

        sales_order.status = "paid"
        sales_order.save()

        print(f"Payment {payment.id} updated to 'succeeded'")
        print(f"Sales Order {sales_order.id} updated to 'paid'")

        if not Invoice.objects.filter(sales_order=sales_order).exists():
            generate_invoice.delay(sales_order.id)
            print(f"Invoice generation triggered for Sales Order {sales_order.id}")

    except Exception as e:
        print(f"ERROR PROCESSING PAYMENT: {str(e)}")
        return JsonResponse({"error": "Error processing payment"}, status=500)

    print("Webhook Processed Successfully")
    return JsonResponse({"message": "Webhook processed successfully"}, status=200)