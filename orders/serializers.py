from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    product_price = serializers.DecimalField(source="product.price", max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ["id","product","product_title","product_price","qty"]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ["id","items"]

class OrderItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    class Meta:
        model = OrderItem
        fields = ["id","product","product_title","price","qty"]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ["id","status","created_at","items"]
