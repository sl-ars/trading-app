from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, TransactionViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='orders')
router.register(r'transactions', TransactionViewSet, basename='transactions')

urlpatterns = [
    #path('webhooks/stripe/', stripe_webhook, name='stripe_webhook'),
    path('', include(router.urls)),
]