from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductCommentsListCreate, CommentUpdateDelete, CommentsMeOrAll

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="products")

urlpatterns = [
    path("", include(router.urls)),
    path("products/<int:product_id>/comments/", ProductCommentsListCreate.as_view()),
    path("comments/<int:pk>/", CommentUpdateDelete.as_view()),
    path("products/comments/", CommentsMeOrAll.as_view()),
]
