from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django_filters.rest_framework import DjangoFilterBackend
import stripe
from ..models import Order, Transaction
from .serializers import OrderSerializer, TransactionSerializer
from products.models import Product, Category
from trading_app.permissions import IsAdmin, IsManager, IsSeller, IsOwnerOrAdmin, IsAdminOrReadOnly
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

# Set Stripe Secret Key
stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    """ Handles Stripe webhook events to confirm payment """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    # Handle the successful payment event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        order_id = session["metadata"]["order_id"]
        order = Order.objects.filter(id=order_id, status="pending").first()

        if order:
            order.status = "paid"
            order.save()
            Transaction.objects.create(order=order, payment_intent_id=session["payment_intent"], payment_status="paid")

    return JsonResponse({"message": "Success"}, status=200)


### ==== DRF API Views (Backend) ==== ###

class OrderViewSet(viewsets.ModelViewSet):
    """
    API for managing customer orders.
    Customers can place orders.
    Admins and managers can manage orders.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['status', 'user__username']

    def get_queryset(self):
        if self.request.user.is_admin() or self.request.user.is_manager():
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        product = serializer.validated_data['product']

        if product.user == self.request.user:
            raise serializers.ValidationError("You cannot purchase your own product.")

        order = serializer.save(user=self.request.user)
        order.calculate_total()

    @swagger_auto_schema(
        method='post',
        operation_description="Creates a Stripe Checkout Session",
        responses={200: openapi.Response("Checkout Session Created")}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def create_checkout_session(self, request, pk=None):
        """ Only the owner can create a Stripe Checkout session for their order """
        order = self.get_object()

        if order.user != request.user:
            return Response({"error": "You are not allowed to pay for this order"}, status=403)

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'kzt',
                    'product_data': {'name': order.product.name},
                    'unit_amount': int(order.total_price * 100),
                },
                'quantity': order.quantity,
            }],
            mode='payment',
            success_url=settings.FRONTEND_URL + f"/orders/{order.id}/success/",
            cancel_url=settings.FRONTEND_URL + f"/orders/{order.id}/payment/",
            metadata={"order_id": order.id}  # Attach order ID for webhook verification
        )

        return Response({"checkout_url": session.url})


    @swagger_auto_schema(
        method='get',
        operation_description="Handle successful payment and mark order as paid",
        responses={200: openapi.Response("Payment Successful")}
    )
    @action(detail=True, methods=['get'], url_path='success', url_name='payment_success_api')
    def payment_success_api(self, request, pk=None):
        """ API endpoint to handle payment success """
        order = get_object_or_404(Order, id=pk)
        order.status = "paid"
        order.save()
        return Response({"message": "Payment successful", "order_id": order.id})



    @swagger_auto_schema(
        method='post',
        operation_description="Cancels a pending order",
        responses={200: openapi.Response("Order Cancelled")}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def cancel(self, request, pk=None):
        """ API endpoint to cancel an order if it's still pending """
        order = self.get_object()
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            return Response({"message": "Order cancelled", "order_id": order.id})
        return Response({"error": "Order cannot be cancelled"}, status=400)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """ Returns transactions of the authenticated user """
        transactions = Transaction.objects.filter(order__user=request.user)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
