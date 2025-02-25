from rest_framework import serializers
from ..models import Order, Transaction
from products.models import Product

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    product_name = serializers.ReadOnlyField(source='product.name')
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    order_id = serializers.ReadOnlyField(source='order.id')
    product_name = serializers.ReadOnlyField(source='order.product.name')

    class Meta:
        model = Transaction
        fields = '__all__'