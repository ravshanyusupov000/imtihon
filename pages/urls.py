from django.urls import path
from .views import home, register_view, login_view, logout_view, product_detail, cart_page, add_to_cart, checkout

urlpatterns = [
    path("", home, name="home"),
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    path("p/<int:pk>/", product_detail, name="product_detail"),

    path("cart/", cart_page, name="cart"),
    path("cart/add/<int:pk>/", add_to_cart, name="add_to_cart"),
    path("checkout/", checkout, name="checkout"),
]
