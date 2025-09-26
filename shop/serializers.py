from rest_framework import serializers
from .models import Product, Order, OrderItem
from django.db import transaction
from decimal import Decimal
from django.contrib.auth import get_user_model



class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','price','stock','description']

class OrderItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id','order','product','product_detail','quantity','price']
        read_only_fields = ['price','product_detail']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ['id','user','total_amount','status','created_at','updated_at','items']
        read_only_fields = ['total_amount','created_at','updated_at']

class AddItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        from .models import Product
        try:
            p = Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
        return value

    def validate(self, attrs):
        from .models import Product
        p = Product.objects.get(pk=attrs['product_id'])
        if attrs['quantity'] > p.stock:
            raise serializers.ValidationError(f"Not enough stock. Available: {p.stock}")
        return attrs

    def save(self, order):
        """
        Creates or updates an OrderItem and reduces product stock.
        """
        from .models import Product, OrderItem
        product = Product.objects.get(pk=self.validated_data['product_id'])
        qty = self.validated_data['quantity']
        price = product.price

        with transaction.atomic():
            # create or update item
            item, created = OrderItem.objects.select_for_update().get_or_create(
                order=order, product=product,
                defaults={'quantity': qty, 'price': price}
            )
            if not created:
                item.quantity += qty
                item.price = price  # update price snapshot if needed
                item.save()

            # decrement stock
            if product.stock < qty:
                raise serializers.ValidationError("Stock changed, not enough left.")
            product.stock -= qty
            product.save()

        return item
