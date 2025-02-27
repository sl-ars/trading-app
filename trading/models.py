from django.db import models
from products.models import Product
from users.models import User


class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('canceled', 'Canceled'),
        ('shipped', 'Shipped'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),

    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        """ Calculates total price from product and quantity """
        self.total_price = self.quantity * self.product.price
        self.save()

    def __str__(self):
        return f"Order {self.id} - {self.user.username} - {self.status}"


class Transaction(models.Model):


    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="transactions")
    timestamp = models.DateTimeField(auto_now_add=True)
    status_from = models.CharField(max_length=20, null=True)
    status_to = models.CharField(max_length=20, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"Transaction {self.id}"
