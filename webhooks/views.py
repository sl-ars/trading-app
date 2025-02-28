from django.shortcuts import get_object_or_404
from django.conf import settings
import stripe
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from sales.models import  Payment, Invoice
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from sales.tasks import generate_invoice

stripe.api_key = settings.STRIPE_SECRET_KEY

@csrf_exempt
def stripe_webhook(request):
    """ Handles Stripe webhook events to update payment status & generate invoice """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        return JsonResponse({"error": "Missing Stripe signature"}, status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Handle different event types
    event_type = event.get("type")

    if event_type in ["checkout.session.completed", "payment_intent.succeeded"]:
        session = event["data"]["object"]

        # Ensure metadata exists
        sales_order_id = session.get("metadata", {}).get("sales_order_id")
        print(session.get("metadata", {}))
        if not sales_order_id:
            return JsonResponse({"error": "Missing sales_order_id"}, status=400)

        # Get Payment & SalesOrder
        payment = get_object_or_404(Payment, sales_order__id=sales_order_id)
        sales_order = payment.sales_order

        # Update payment status
        payment.status = "succeeded"
        payment.save()

        # Generate invoice asynchronously (Celery Task)
        if not Invoice.objects.filter(sales_order=sales_order).exists():
            generate_invoice.delay(sales_order.id)

    elif event_type == "payment_intent.payment_failed":
        session = event["data"]["object"]
        sales_order_id = session.get("metadata", {}).get("sales_order_id")

        if sales_order_id:
            payment = Payment.objects.filter(sales_order__id=sales_order_id).first()
            if payment:
                payment.status = "failed"
                payment.save()

    return JsonResponse({"message": "Webhook processed successfully"}, status=200)
