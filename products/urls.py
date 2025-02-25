from django.urls import path, include
from .views import (

    product_list, product_create, product_detail,
     product_edit, product_delete, user_listings
)



urlpatterns = [
    path('listings/', product_list, name='product_list'),
    path('create/', product_create, name='product_create'),
    path('my/', user_listings, name='user_listings'),
    path('<int:product_id>/', product_detail, name='product_detail'),
    path('<int:product_id>/edit/', product_edit, name='product_edit'),
    path('<int:product_id>/delete/', product_delete, name='product_delete'),
]