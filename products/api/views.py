from rest_framework import viewsets, permissions, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from products.api.serializers import ProductSerializer, CategorySerializer
from ..models import Product, Category
from trading_app.permissions import IsAdmin, IsManager, IsSeller, IsOwnerOrAdmin, IsAdminOrReadOnly

### ==== DRF API Views (Backend) ==== ###

class CategoryViewSet(viewsets.ModelViewSet):
    """ API for managing product categories """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class ProductViewSet(viewsets.ModelViewSet):
    """
    API for managing product listings.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['title', 'description', 'category__name']
    filterset_fields = ['category']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """ Assigns the logged-in user to the listing """
        serializer.save(user=self.request.user)

    def get_permissions(self):
        """ Assign permissions dynamically based on user role """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsOwnerOrAdmin() if self.request.user.is_seller() else IsManager()]
        return [permissions.AllowAny()]


    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_listings(self, request):
        """ Returns only the listings created by the authenticated user """
        user_listings = Product.objects.filter(user=request.user)
        serializer = self.get_serializer(user_listings, many=True)
        return Response(serializer.data)