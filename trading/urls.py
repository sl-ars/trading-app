from django.urls import path, include
from .views import (
main_page,  order_list, order_detail, transaction_list,
create_order, payment_page, payment_success,
cancel_order
)

urlpatterns = [
    path('', main_page, name='main_page'),
    path('orders/', order_list, name='order_list'),
    path('orders/<int:order_id>/', order_detail, name='order_detail'),
    path('orders/<int:order_id>/success/', payment_success, name='payment_success'),
    path('transactions/', transaction_list, name='transaction_list'),
    path('orders/create/<int:product_id>/', create_order, name='create_order'),
    path('orders/<int:order_id>/payment/', payment_page, name='payment_page'),
    path('orders/<int:order_id>/cancel/', cancel_order, name='cancel_order'),
]