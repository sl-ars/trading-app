from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
import stripe
from sales.models import SalesOrder, Payment, Invoice
from sales.serializers import SalesOrderSerializer, PaymentSerializer, InvoiceSerializer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from trading.models import Order
from trading_app.permissions import IsCustomer, IsTrader
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from sales.tasks import generate_invoice

stripe.api_key = settings.STRIPE_SECRET_KEY


class SalesOrderViewSet(viewsets.ModelViewSet):
    """
    API for managing sales orders.
    - Customers can pay after trader approval.
    - Traders can manage shipments after payment.
    """
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ Filter SalesOrders based on role """
        if getattr(self, 'swagger_fake_view', False):
            return SalesOrder.objects.none()

        user = self.request.user
        if user.is_trader():
            return SalesOrder.objects.filter(order__product__user=user)
        return SalesOrder.objects.filter(order__user=user)

    def create_or_get_sales_order(self, order):
        """ Create a SalesOrder if it doesn't exist """
        sales_order, created = SalesOrder.objects.get_or_create(order=order)
        return sales_order

    @swagger_auto_schema(
        method='post',
        operation_description="Create a Stripe payment session for an approved SalesOrder",
        responses={200: "Stripe Checkout Session Created"}
    )
    @action(detail=False, methods=['post'], permission_classes=[IsCustomer])
    def create_payment_session(self, request):
        """ Create or retrieve SalesOrder and process payment """

        order_id = request.data.get("orderId")

        if not order_id:
            return Response({"error": "Missing orderId."}, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(Order, id=order_id)

        if order.status != "approved":
            return Response({"error": "Payment can only be made for approved orders."},
                            status=status.HTTP_400_BAD_REQUEST)

        sales_order = self.create_or_get_sales_order(order)

        frontend_base_url = settings.FRONTEND_URL

        # Auto-mark paid if DEBUG is True
        if settings.DEBUG:
            sales_order.status = "paid"
            sales_order.save()
            ##self.generate_invoice(sales_order)
            #return Response({"message": "DEBUG Mode: Order automatically marked as paid."}, status=status.HTTP_200_OK)

        # Create Stripe Checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'kzt',
                    'product_data': {'name': sales_order.order.product.title},
                    'unit_amount': int(sales_order.order.total_price * 100),
                },
                'quantity': sales_order.order.quantity,
            }],
            mode='payment',
            success_url=f"{frontend_base_url}/orders/{order.id}/success/",
            cancel_url=f"{frontend_base_url}/orders/{order.id}/cancel/",
            payment_intent_data={
                "metadata": {"sales_order_id": str(sales_order.id)}
            }
        )

        # Store Payment Intent
        payment, created = Payment.objects.get_or_create(sales_order=sales_order)
        payment.payment_intent_id = session.id
        payment.status = "pending"
        payment.save()

        return Response({"checkout_url": session.url})

    @action(detail=True, methods=['post'], permission_classes=[IsTrader])
    def mark_as_shipped(self, request, pk=None):
        """ Traders can mark an order as shipped after payment """
        sales_order = self.get_object()

        if sales_order.order.product.user != request.user:
            return Response({"error": "You cannot mark this order as shipped"}, status=status.HTTP_403_FORBIDDEN)

        if sales_order.status != "paid":
            return Response({"error": "Only paid orders can be marked as shipped"}, status=status.HTTP_400_BAD_REQUEST)

        sales_order.status = "shipped"
        sales_order.save()



        return Response({"message": "Order marked as shipped", "sales_order_id": sales_order.id})


    @action(detail=True, methods=['post'], permission_classes=[IsTrader])
    def mark_as_paid(self, request, pk=None):
        """Mark an order as paid (only for testing/debugging)"""
        sales_order = self.get_object()

        if sales_order.status != "approved":
            return Response({"error": "Only approved orders can be marked as paid"}, status=status.HTTP_400_BAD_REQUEST)

        sales_order.status = "paid"
        sales_order.save()

        generate_invoice.delay(sales_order.id)

        return Response({"message": "Order marked as paid, invoice is being generated."})


class PaymentViewSet(viewsets.ModelViewSet):
    """ API for managing payments """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):

        """ Returns only payments related to the user's sales orders """
        if getattr(self, 'swagger_fake_view', False):
            return Payment.objects.none()

        return Payment.objects.filter(sales_order__order__user=self.request.user)

class InvoiceViewSet(viewsets.ModelViewSet):
    """ API for managing invoices """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ Returns only invoices related to the user's sales orders """
        if getattr(self, 'swagger_fake_view', False):
            return Invoice.objects.none()

        return Invoice.objects.filter(sales_order__order__user=self.request.user)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Create an invoice and trigger PDF generation."""
        sales_order_id = request.data.get("sales_order")

        if not sales_order_id:
            return Response({"error": "Missing sales_order ID"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            sales_order = SalesOrder.objects.select_related('order', 'order__user', 'order__product').get(
                id=sales_order_id)
            print(f"Sales Order Found: {sales_order}")
        except SalesOrder.DoesNotExist:
            return Response({"error": "Sales Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Permission Check
        if (
                sales_order.order.user != request.user and
                sales_order.order.product.user != request.user and
                not request.user.is_admin()
        ):
            return Response(
                {"error": "You do not have permission to generate this invoice."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Avoid Duplicate Invoice
        if Invoice.objects.filter(sales_order=sales_order).exists():
            return Response({"error": "Invoice already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Create Invoice Entry
        invoice = Invoice.objects.create(sales_order=sales_order)
        print(f"Invoice Created: {invoice.id}")

        # Asynchronous Task for Invoice Generation
        generate_invoice.apply_async(args=[sales_order.id])

        return Response(
            {"message": "Invoice is being generated. Please check again later.", "invoice_id": invoice.id},
            status=status.HTTP_202_ACCEPTED
        )