from django.db import models
from django.conf import settings
from trading.models import Order
from django.utils.timezone import now

class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="sales_order")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sales Order {self.id} for Order {self.order.id} - {self.status}"


class Invoice(models.Model):

    sales_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, related_name="invoice", null=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to="invoices/", blank=True, null=True)

    def __str__(self):
        return f"Invoice for Sales Order {self.sales_order.id}"


class Payment(models.Model):

    PAYMENT_METHODS = [
        ('stripe', 'Stripe')
    ]

    sales_order = models.OneToOneField(SalesOrder, on_delete=models.CASCADE, related_name="payment", null=True)
    method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='stripe')
    payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Sales Order {self.sales_order.id} - {self.status}"