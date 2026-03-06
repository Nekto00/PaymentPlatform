from rest_framework import serializers

from apps.accounts.serializers import UserProfileSerializer

from .models import Category, Comment, Post


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description"]


class CommentSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "user", "content", "created_at", "is_approved"]
        read_only_fields = ["user", "is_approved"]


class PostSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source="category",
        write_only=True,
        required=False,
        allow_null=True,
    )
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "excerpt",
            "author",
            "category",
            "category_id",
            "is_paid",
            "price",
            "status",
            "views_count",
            "created_at",
            "updated_at",
            "published_at",
            "comments",
        ]
        read_only_fields = ["slug", "views_count"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
