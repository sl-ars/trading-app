from django.db import models
from products.models import Product
from users.models import User

from django.utils.timezone import now

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),

    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    stripe_payment_intent = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        """ Calculates total price from product and quantity """
        self.total_price = self.quantity * self.product.price
        self.save()

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"


class Transaction(models.Model):
    PAYMENT_CHOICES = (
        ('card', 'Card'),
        ('cash', 'Cash'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="transaction")
    payment_intent_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='card')
    payment_status = models.CharField(max_length=10, choices=(('paid', 'Paid'), ('failed', 'Failed')), default='paid')
    created_at = models.DateTimeField(default=now, blank=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.payment_status}"
