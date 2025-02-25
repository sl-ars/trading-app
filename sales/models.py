from django.db import models
from trading.models import Order

class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    invoice_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.order.user.username}"

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.order.id} - {self.status}"