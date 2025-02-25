from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Product)
class ProductListingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', 'user', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    ordering = ('-created_at',)