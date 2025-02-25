from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'role')
    list_filter = ('role', 'is_active', 'is_staff')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role',)}),
    )