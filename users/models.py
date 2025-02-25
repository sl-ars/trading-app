from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with roles for Role-Based Access Control (RBAC).
    """
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('seller', 'Seller'),
        ('customer', 'Customer'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def is_manager(self):
        return self.role == 'manager'

    def is_seller(self):
        return self.role == 'seller'

    def is_customer(self):
        return self.role == 'customer'

    def __str__(self):
        return self.username
