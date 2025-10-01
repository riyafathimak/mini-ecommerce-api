from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import ProductViewSet, OrderViewSet
from .views import TotalOrderSummaryView
from . import views

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('orders-summary/', TotalOrderSummaryView.as_view(), name='orders-summary'),
    #path('orders/export/csv/', views.export_orders_csv, name='export_orders_csv'),
    #path('orders/export/excel/', views.export_orders_excel, name='export_orders_excel'),
     # other routes...
    #path('orders/export/excel/', views.export_orders_excel, name='export_orders_excel'),
    # if you still want CSV:
    path('orders/export/csv/', views.export_orders_csv, name='export_orders_csv'),
    path('orders/export/excel/', views.export_orders_excel, name='export_orders_excel'),

]



