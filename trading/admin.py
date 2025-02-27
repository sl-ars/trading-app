from django.contrib import admin
from trading.models import Order, Transaction

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'status', 'total_price', 'created_at')
    search_fields = ('user__username', 'product__title', 'status')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'status_from', 'status_to', 'timestamp')
    search_fields = ('order__id', 'user__username', 'status_from', 'status_to')