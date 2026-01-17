from rest_framework import serializers
from .models import Product, Category, Comment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name"]

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Product
        fields = ["id","title","description","price","image","is_active","category","category_id","created_at"]

    def create(self, validated_data):
        cid = validated_data.pop("category_id", None)
        if cid:
            validated_data["category_id"] = cid
        return super().create(validated_data)

    def update(self, instance, validated_data):
        cid = validated_data.pop("category_id", None)
        if cid is not None:
            instance.category_id = cid
        return super().update(instance, validated_data)

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id","product","user","parent","text","created_at","replies"]
        read_only_fields = ["product","user","created_at","replies"]

    def get_replies(self, obj):
        qs = obj.replies.all().order_by("created_at")
        return CommentSerializer(qs, many=True).data
