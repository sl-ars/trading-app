from rest_framework import serializers
from sales.models import SalesOrder, Payment, Invoice

class SalesOrderSerializer(serializers.ModelSerializer):
    """ Serializer for Sales Orders """

    class Meta:
        model = SalesOrder
        fields = ('id', 'order', 'total_price', 'status', 'created_at')
        read_only_fields = ('id', 'total_price', 'created_at')


class PaymentSerializer(serializers.ModelSerializer):
    """ Serializer for Payments """

    class Meta:
        model = Payment
        fields = ('id', 'sales_order', 'method', 'payment_intent_id', 'status', 'created_at')
        read_only_fields = ('id', 'created_at')


class InvoiceSerializer(serializers.ModelSerializer):
    """ Serializer for Invoices """

    class Meta:
        model = Invoice
        fields = ('id', 'sales_order', 'issued_at', 'pdf_file')
        read_only_fields = ('id', 'issued_at')