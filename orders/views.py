from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction

from .models import Cart, CartItem, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer

def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

class CartView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get_object(self):
        return get_or_create_cart(self.request.user)

class CartAdd(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = get_or_create_cart(request.user)
        product_id = request.data.get("product")
        qty = int(request.data.get("qty", 1))
        item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
        item.qty = item.qty + qty if not created else qty
        item.save()
        return Response({"ok": True})

class CartRemove(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        cart = get_or_create_cart(request.user)
        product_id = request.data.get("product")
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        return Response({"ok": True})

class CartClear(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        cart = get_or_create_cart(request.user)
        cart.items.all().delete()
        return Response({"ok": True})

class CartUpdateQty(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def patch(self, request):
        cart = get_or_create_cart(request.user)
        item_id = request.data.get("item_id")
        qty = int(request.data.get("qty", 1))
        CartItem.objects.filter(cart=cart, id=item_id).update(qty=max(qty, 1))
        return Response({"ok": True})

class OrderCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart = get_or_create_cart(request.user)
        items = cart.items.select_related("product")
        if not items.exists():
            return Response({"detail": "Cart empty"}, status=400)

        order = Order.objects.create(user=request.user)
        for ci in items:
            OrderItem.objects.create(
                order=order,
                product=ci.product,
                price=ci.product.price,
                qty=ci.qty
            )
        items.delete()
        return Response(OrderSerializer(order).data, status=201)

class OrdersList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

class OrderDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

class OrderStatusUpdate(APIView):
    permission_classes = [permissions.IsAdminUser]
    def patch(self, request, pk):
        status_val = request.data.get("status")
        Order.objects.filter(id=pk).update(status=status_val)
        return Response({"ok": True})

class OrderCancel(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def delete(self, request, pk):
        Order.objects.filter(id=pk, user=request.user).update(status=Order.CANCELED)
        return Response({"ok": True})
