from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from products.models import Product, Category
from products.serializers import ProductSerializer, CategorySerializer
from trading_app.permissions import IsTrader, IsAdminOrReadOnly, IsOwnerOrAdmin
from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

class ProductViewSet(viewsets.ModelViewSet):
    """
    API for managing products.
    - Traders can create, update, and delete their own products.
    - Customers can only view available products.
    """
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price']
    search_fields = ['title', 'description']
    pagination_class = ProductPagination

    def get_permissions(self):
        """ Set RBAC for product management """
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'my_listings']:
            return [IsTrader(), IsOwnerOrAdmin()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        """ Assign trader as the owner of the product """
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        method='get',
        operation_description="Retrieve all products in a category",
        responses={200: openapi.Response("List of products in the category")}
    )
    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_id>[^/.]+)')
    def get_by_category(self, request, category_id=None):
        """ Get products filtered by category """
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(category=category)
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        method="get",
        operation_description="Retrieve products created by the authenticated user",
        responses={200: ProductSerializer(many=True)}
    )
    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def my_listings(self, request):
        """ Get listings specific to the authenticated trader """
        user = request.user
        if not user.is_trader():
            return Response({"error": "Only traders can view their listings"}, status=403)

        queryset = Product.objects.filter(user=user).order_by("-created_at")

        # Apply filtering dynamically
        category = request.query_params.get("category")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

        if category:
            queryset = queryset.filter(category_id=category)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    API for managing product categories.
    - Admins can create, update, and delete categories.
    - Customers and traders can view categories.
    - Supports filtering and search.
    """
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]
    pagination_class = None

    def get_queryset(self):
        """ Only return active categories """
        return Category.objects.all().order_by("name")