from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ProductViewSet, OrderViewSet
from .views import TotalOrderSummaryView


router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('orders-summary/', TotalOrderSummaryView.as_view(), name='orders-summary'),
]

