from django.urls import path, include
from rest_framework.routers import DefaultRouter
from sales.views import SalesOrderViewSet, PaymentViewSet, InvoiceViewSet, stripe_webhook

router = DefaultRouter()
router.register(r'sales-orders', SalesOrderViewSet, basename='sales_orders')
router.register(r'payments', PaymentViewSet, basename='payments')
router.register(r'invoices', InvoiceViewSet, basename='invoices')

urlpatterns = [
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    path('', include(router.urls)),
]