from django.urls import path, include

urlpatterns = [
    path('trading/', include('trading.api.urls')),
    path('users/', include('users.urls')),
    path('products/', include('products.api.urls')),
]