from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from products.models import Product
from sales.models import SalesOrder
from trading.models import Order, Transaction
from trading.serializers import OrderSerializer, TransactionSerializer
from trading_app.permissions import IsOwnerOrAdmin, IsCustomer, IsTrader


class OrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderViewSet(viewsets.ModelViewSet):
    """
    API for managing customer orders.
    - Customers request an order (pending).
    - The trader (who owns the product) approves or rejects.
    - The customer pays, then the trader ships.
    """
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['status', 'user__username']
    pagination_class = OrderPagination

    def get_queryset(self):
        """Filter orders based on user role"""
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        user = self.request.user
        if user.is_trader():
            return Order.objects.filter(product__user=user)
        return Order.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        """Customers request an order (needs trader approval)"""
        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        if not product_id:
            return Response({"error": "Product ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)

        if product.user == request.user:
            return Response({"error": "You cannot purchase your own product."}, status=status.HTTP_400_BAD_REQUEST)

        if product.stock < int(quantity):
            return Response({"error": "Not enough stock available"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the order
        order = Order.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            total_price=product.price * int(quantity)
        )

        # Send notification to the trader
        self.send_notification(product.user, {
            "message": f"New order request for {product.title}. Approve or reject.",
            "order_id": order.id,
            "product": product.title
        })

        return Response({
            "id": order.id,
            "status": order.status,
            "total_price": str(order.total_price),
            "message": "Order request sent to trader for approval."
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[IsTrader])
    def approve(self, request, pk=None):
        """Trader (who owns the product) approves an order"""
        order = self.get_object()

        if order.status != 'pending':
            return Response({"error": "Only pending orders can be approved"}, status=status.HTTP_400_BAD_REQUEST)

        if order.product.user != request.user:
            return Response({"error": "You cannot approve this order"}, status=status.HTTP_403_FORBIDDEN)

        order.status = "approved"
        order.save()

        # Log transaction
        Transaction.objects.create(
            order=order,
            user=request.user,
            status_from="pending",
            status_to="approved"
        )

        # Notify customer
        self.send_notification(order.user, {
            "message": f"Your order for {order.product.title} has been approved.",
            "order_id": order.id,
            "product": order.product.title
        })

        return Response({"message": "Order approved", "order_id": order.id})

    @action(detail=True, methods=['post'], permission_classes=[IsTrader])
    def reject(self, request, pk=None):
        """Trader (who owns the product) rejects an order"""
        order = self.get_object()

        if order.status != 'pending':
            return Response({"error": "Only pending orders can be rejected"}, status=status.HTTP_400_BAD_REQUEST)

        if order.product.user != request.user:
            return Response({"error": "You cannot reject this order"}, status=status.HTTP_403_FORBIDDEN)

        order.status = "rejected"
        order.save()

        # Log transaction
        Transaction.objects.create(
            order=order,
            user=request.user,
            status_from="pending",
            status_to="rejected"
        )

        # Notify customer
        self.send_notification(order.user, {
            "message": f"Your order for {order.product.title} has been rejected.",
            "order_id": order.id,
            "product": order.product.title
        })

        return Response({"message": "Order rejected", "order_id": order.id})

    @action(detail=True, methods=['post'], permission_classes=[IsTrader])
    def ship(self, request, pk=None):
        """Trader can only ship an order after successful payment"""
        order = self.get_object()

        if order.status != 'paid':
            return Response({"error": "You can only ship paid orders"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify payment exists in SalesOrder
        sales_order = SalesOrder.objects.filter(order=order, status="succeeded").first()
        if not sales_order:
            return Response({"error": "Order has not been paid yet"}, status=status.HTTP_400_BAD_REQUEST)

        order.status = "shipped"
        order.save()

        # Log transaction
        Transaction.objects.create(
            order=order,
            user=request.user,
            status_from="paid",
            status_to="shipped"
        )

        # Notify customer
        self.send_notification(order.user, {
            "message": f"Your order for {order.product.title} has been shipped.",
            "order_id": order.id,
            "product": order.product.title
        })

        return Response({"message": "Order shipped", "order_id": order.id})

    @staticmethod
    def send_notification(user, data):
        """Sends a notification via WebSocket"""
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}", {"type": "notify", "notification": data}
        )


class TransactionViewSet(viewsets.ModelViewSet):
    """API for tracking order status changes"""
    queryset = Transaction.objects.all().select_related("order", "user")
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['order__id', 'status_from', 'status_to', 'user__username']

    def get_queryset(self):
        """Filter transactions based on user role"""
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        user = self.request.user
        if user.is_trader():
            return Transaction.objects.filter(order__product__user=user)
        return Transaction.objects.filter(order__user=user)