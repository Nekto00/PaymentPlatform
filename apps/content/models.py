from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Post(models.Model):
    POST_STATUS = (
        ("draft", "Черновик"),
        ("published", "Опубликован"),
        ("archived", "Архивный"),
    )

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    slug = models.SlugField(unique=True, verbose_name="URL")
    content = models.TextField(verbose_name="Содержание")
    excerpt = models.TextField(
        max_length=500, blank=True, verbose_name="Краткое описание"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts", verbose_name="Автор"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Категория",
    )

    # УПРОЩАЕМ: только булево поле - бесплатно или по подписке
    is_paid = models.BooleanField(default=False, verbose_name="Только по подписке")

    # Убираем price и payment_type

    status = models.CharField(
        max_length=20, choices=POST_STATUS, default="draft", verbose_name="Статус"
    )
    views_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    published_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Дата публикации"
    )

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Генерируем slug из заголовка, если его нет
        if not self.slug:
            import uuid

            from django.utils.text import slugify

            base_slug = slugify(self.title)[:50]
            if not base_slug:
                base_slug = "post"

            self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"

        if self.status == "published" and not self.published_at:
            from django.utils import timezone

            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def increment_views(self):
        self.views_count += 1
        self.save(update_fields=["views_count"])


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments", verbose_name="Пост"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пользователь",
    )
    content = models.TextField(verbose_name="Комментарий")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Комментарий от {self.user.phone_number} к посту {self.post.title}"
