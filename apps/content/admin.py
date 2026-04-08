from django.contrib import admin

from .models import Category, Comment, Post


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "is_paid",
        "status",
        "views_count",
        "created_at",
    )
    list_filter = ("status", "is_paid", "category")
    search_fields = ("title", "content")
    prepopulated_fields = {"slug": ("title",)}
    raw_id_fields = ("author",)
    list_editable = ("status", "is_paid")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "user", "short_content", "is_approved", "created_at")
    list_filter = ("is_approved", "created_at")
    search_fields = ("content", "user__phone_number", "post__title")
    list_editable = ("is_approved",)
    actions = ["approve_comments", "disapprove_comments"]

    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    short_content.short_description = "Комментарий" # type: ignore

    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"✅ Одобрено {queryset.count()} комментариев")

    approve_comments.short_description = "Одобрить выбранные комментарии" # type: ignore

    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, f"❌ Заблокировано {queryset.count()} комментариев")

    disapprove_comments.short_description = "Заблокировать выбранные комментарии" # type: ignore
