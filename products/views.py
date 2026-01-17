from rest_framework import viewsets, permissions, filters, generics
from .models import Product, Comment
from .serializers import ProductSerializer, CommentSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET","HEAD","OPTIONS"):
            return True
        return request.user and request.user.is_staff

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).order_by("-created_at")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ["title","description"]

class ProductCommentsListCreate(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        pid = self.kwargs["product_id"]
        return Comment.objects.filter(product_id=pid, parent__isnull=True).order_by("-created_at")

    def perform_create(self, serializer):
        pid = self.kwargs["product_id"]
        serializer.save(product_id=pid, user=self.request.user)

class CommentUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

class CommentsMeOrAll(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Comment.objects.all().order_by("-created_at")
        return Comment.objects.filter(user=self.request.user).order_by("-created_at")
