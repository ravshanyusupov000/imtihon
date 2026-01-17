from django.urls import path
from .views import (
    CartView, CartAdd, CartRemove, CartClear, CartUpdateQty,
    OrderCreate, OrdersList, OrderDetail, OrderStatusUpdate, OrderCancel
)

urlpatterns = [
    path("cart/", CartView.as_view()),
    path("cart/add/", CartAdd.as_view()),
    path("cart/remove/", CartRemove.as_view()),
    path("cart/clear/", CartClear.as_view()),
    path("cart/update/", CartUpdateQty.as_view()),

    path("order/create/", OrderCreate.as_view()),
    path("orders/", OrdersList.as_view()),
    path("orders/<int:pk>/", OrderDetail.as_view()),
    path("orders/<int:pk>/status/", OrderStatusUpdate.as_view()),
    path("orders/<int:pk>/cancel/", OrderCancel.as_view()),
]
