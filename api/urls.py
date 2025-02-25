from django.urls import path, include

urlpatterns = [
    path('trading/', include('trading.api.urls')),
    path('user/', include('users.api.urls')),
    path('products/', include('products.api.urls')),
]