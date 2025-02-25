"""
URL configuration for trading_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.routers import DefaultRouter
from rest_framework.permissions import AllowAny




urlpatterns = [

    # Template-based URLs (Frontend)
    path('admin/', admin.site.urls),
    path('products/', include('products.urls')),
    path('user/', include('users.urls')),
    path('', include('trading.urls')),
    path('sales/', include('sales.urls')),
    path('analytics/', include('analytics.urls')),
    path('notifications/', include('notifications.urls')),

    # API URLs (Backend)
    path('api/', include('api.urls')),
]


jwt_authentication = openapi.Parameter(
    'Authorization',
    in_=openapi.IN_HEADER,
    description='JWT token authentication using Bearer token.',
    type=openapi.TYPE_STRING,
    required=True,
)

# Swagger schema view
schema_view = get_schema_view(
   openapi.Info(
      title="Trading App API",
      default_version='v1',
      description="API documentation for the Trading App",
      terms_of_service="",
      contact=openapi.Contact(email="sl.ars@icloud.com"),
      license=openapi.License(name="MIT"),
   ),
   public=True,
permission_classes=(AllowAny,),
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='swagger-schema'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='swagger-redoc')
]
