from rest_framework import serializers

from products.serializers import ProductSerializer
from trading.models import Order, Transaction
from products.models import Product

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    product = ProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    sales_status = serializers.SerializerMethodField()
    shipping_address = serializers.CharField(source="user.profile.shipping_address", read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "product",
            "quantity",
            "total_price",
            "status",
            "sales_status",
            "shipping_address",
            "created_at",
        ]

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "username": obj.user.username,
            "email": obj.user.email
        }

    def get_sales_status(self, obj):
        return obj.sales_order.status if hasattr(obj, "sales_order") and obj.sales_order else "Not Paid"

class TransactionSerializer(serializers.ModelSerializer):
    order_id = serializers.ReadOnlyField(source='order.id')
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'