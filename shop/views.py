from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Product, Order, OrderItem
from .serializers import ProductSerializer, OrderSerializer, OrderItemSerializer, AddItemSerializer
from .filters import ProductFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from rest_framework import generics, viewsets, status
from .models import Product, Order, OrderItem
from django.contrib.auth.models import User
from rest_framework import serializers


class ProductViewSet(viewsets.ModelViewSet):
    """
    Products CRUD + search + filter by price range
    Search fields: name, description
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'stock']

class OrderViewSet(viewsets.ModelViewSet):
    """
    Orders CRUD. user is set from request.user on create.
    """
    queryset = Order.objects.all().select_related('user').prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users see their own orders. Admins can see all.
        user = self.request.user
        if user.is_staff:
            return Order.objects.all().prefetch_related('items')
        return Order.objects.filter(user=user).prefetch_related('items')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


    @action(detail=True, methods=['post'], url_path='add-items')
    def add_items(self, request, pk=None):
        """
        POST /orders/{id}/add-items/
        {
          "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 3, "quantity": 5}
          ]
        }
        """
        order = self.get_object()
        if order.status != Order.STATUS_PENDING:
            return Response(
                {"detail": "Items can be added only to pending orders."},
                status=status.HTTP_400_BAD_REQUEST
            )

        items_data = request.data.get("items", [])
        if not isinstance(items_data, list):
            return Response(
                {"detail": "Expected a list of items."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_items = []
        for item_data in items_data:
            serializer = AddItemSerializer(data=item_data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            try:
                item = serializer.save(order=order)
                created_items.append(OrderItemSerializer(item).data)
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(created_items, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='change-status')
    def change_status(self, request, pk=None):
        """
        Change order status. payload: { "status": "paid" }
        """
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({"detail":"Invalid status."}, status=status.HTTP_400_BAD_REQUEST)
        # optionally add business rules e.g. can't go from pending -> shipped directly
        order.status = new_status
        order.save(update_fields=['status'])
        return Response(self.get_serializer(order).data)
    
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('id','username','password','email')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            password=validated_data['password']
        )
        return user

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer