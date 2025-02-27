from rest_framework import serializers
from sales.models import SalesOrder, Payment, Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    """ Serializer for Invoices """

    pdf_file = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ("id", "sales_order", "issued_at", "pdf_file")
        read_only_fields = ("id", "issued_at")

    def get_pdf_file(self, obj):

        return obj.get_download_url() if obj.pdf_file else None


class SalesOrderSerializer(serializers.ModelSerializer):
    """ Serializer for Sales Orders """
    invoice = serializers.SerializerMethodField()

    class Meta:
        model = SalesOrder
        fields = ("id", "order", "total_price", "status", "created_at", "invoice")
        read_only_fields = ("id", "total_price", "created_at")

    def get_invoice(self, obj):
        if hasattr(obj, "invoice") and obj.invoice:
            return InvoiceSerializer(obj.invoice).data
        return None


class PaymentSerializer(serializers.ModelSerializer):
    """ Serializer for Payments """

    class Meta:
        model = Payment
        fields = ("id", "sales_order", "method", "payment_intent_id", "status", "created_at")
        read_only_fields = ("id", "created_at")