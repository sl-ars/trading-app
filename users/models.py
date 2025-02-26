from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.timezone import now
from users.storage import AvatarStorage

class User(AbstractUser):
    """
    Custom user model with Role-Based Access Control (RBAC).
    Roles: Admin, Trader, Sales Representative, Customer.
    """

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('trader', 'Trader'),
        ('sales_rep', 'Sales Representative'),
        ('customer', 'Customer'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True, help_text="Phone number")
    avatar = models.ImageField(storage=AvatarStorage(), upload_to="avatars/", blank=True, null=True, help_text="Profile picture")
    date_joined = models.DateTimeField(default=now, editable=False, help_text="Date of registration")
    last_updated = models.DateTimeField(auto_now=True, help_text="Last profile update")

    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    def is_trader(self):
        return self.role == 'trader'

    def is_sales_rep(self):
        return self.role == 'sales_rep'

    def is_customer(self):
        return self.role == 'customer'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"