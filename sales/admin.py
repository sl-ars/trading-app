from django.contrib import admin
from sales.models import SalesOrder, Payment, Invoice

@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'total_price', 'status', 'created_at')
    search_fields = ('order__user__username', 'status')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'sales_order', 'method', 'status', 'created_at')
    search_fields = ('sales_order__order__user__username', 'status')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'sales_order', 'issued_at', 'pdf_file')
    search_fields = ('sales_order__order__user__username',)