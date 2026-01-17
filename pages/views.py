from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from products.models import Product, Comment
from orders.models import Cart, CartItem, Order, OrderItem
from django.db import transaction

User = get_user_model()

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username") or "user"
        email_or_phone = request.POST.get("email_or_phone","").strip()
        password = request.POST.get("password","")

        user = User(username=username)
        if "@" in email_or_phone:
            user.email = email_or_phone.lower()
        else:
            user.phone = email_or_phone
        user.set_password(password)
        user.save()
        return redirect("login")
    return render(request, "pages/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect("/admin/")
            return redirect("home")
    return render(request, "pages/login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

from collections import defaultdict
from products.models import Category, Product

@login_required(login_url="login")
def home(request):
    if request.user.is_staff:
        return redirect("/admin/")

    cat_id = request.GET.get("cat")

    qs = Product.objects.filter(is_active=True).select_related("category").order_by("category__name", "-created_at")
    if cat_id:
        qs = qs.filter(category_id=cat_id)

    grouped = defaultdict(list)
    for p in qs:
        grouped[p.category].append(p)  # category None bo'lishi ham mumkin

    all_categories = Category.objects.all().order_by("name")
    selected_cat = int(cat_id) if cat_id and cat_id.isdigit() else None

    return render(request, "pages/home.html", {
        "grouped": dict(grouped),
        "all_categories": all_categories,
        "selected_cat": selected_cat,
    })


@login_required
def product_detail(request, pk):
    p = get_object_or_404(Product, pk=pk, is_active=True)

    if request.method == "POST":
        text = request.POST.get("text","").strip()
        parent_id = request.POST.get("parent")
        if text:
            Comment.objects.create(
                product=p,
                user=request.user,
                text=text,
                parent_id=parent_id or None
            )
        return redirect("product_detail", pk=pk)

    root_comments = Comment.objects.filter(product=p, parent__isnull=True).order_by("-created_at")
    return render(request, "pages/detail.html", {"p": p, "comments": root_comments})

def _get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

@login_required
def cart_page(request):
    cart = _get_cart(request.user)
    items = cart.items.select_related("product")
    total = sum([i.product.price * i.qty for i in items])
    return render(request, "pages/cart.html", {"items": items, "total": total})

@login_required
def add_to_cart(request, pk):
    cart = _get_cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product_id=pk)
    item.qty = item.qty + 1 if not created else 1
    item.save()
    return redirect("cart")

@login_required
@transaction.atomic
def checkout(request):
    cart = _get_cart(request.user)
    items = cart.items.select_related("product")
    if not items.exists():
        return redirect("cart")

    order = Order.objects.create(user=request.user)
    for ci in items:
        OrderItem.objects.create(order=order, product=ci.product, price=ci.product.price, qty=ci.qty)
    items.delete()
    return render(request, "pages/checkout_done.html", {"order": order})
