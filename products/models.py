from django.db import models
from .storage import ProductStorage
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product Model with image upload.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products", help_text="Owner of the product listing.")
    title = models.CharField(max_length=255, help_text="Name of the product.")
    description = models.TextField(blank=True, null=True, help_text="Detailed description of the product.")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the product in KZT.")
    stock = models.PositiveIntegerField(default=0, help_text="Available stock quantity.")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", help_text="Category of the product.")
    image = models.ImageField(storage=ProductStorage(), upload_to='products/', blank=True, null=True, help_text="Product image.")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Date and time when the product was added.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp.")

    def __str__(self):
        return f"{self.title} - {self.price} KZT"

    def reduce_stock(self, quantity):
        """ Reduce stock when an order is placed """
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    def increase_stock(self, quantity):
        """ Increase stock when an order is canceled """
        self.stock += quantity
        self.save()