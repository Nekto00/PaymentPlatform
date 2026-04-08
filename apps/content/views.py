from datetime import timezone

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .forms import CommentForm, PostForm, PostSearchForm
from .models import Category, Post
from .serializers import CategorySerializer, CommentSerializer, PostSerializer


def post_list(request):
    form = PostSearchForm(request.GET)
    posts = Post.objects.filter(status="published")

    if form.is_valid():
        query = form.cleaned_data.get("query")
        category = form.cleaned_data.get("category")
        is_paid = form.cleaned_data.get("is_paid")

        if query:
            posts = posts.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(excerpt__icontains=query)
            )

        if category:
            posts = posts.filter(category=category)

        if is_paid == "paid":
            posts = posts.filter(is_paid=True)
        elif is_paid == "free":
            posts = posts.filter(is_paid=False)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "form": form,
        "categories": Category.objects.all(),
        "request": request,
    }
    return render(request, "content/post_list.html", context)


def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status="published")
    has_access = True

    # Проверка доступа для платных постов
    if post.is_paid:
        if not request.user.is_authenticated:
            has_access = False
            messages.warning(
                request,
                "🔒 Этот пост доступен только по подписке. Пожалуйста, войдите в систему.",
            )
        elif not request.user.has_paid_subscription:
            has_access = False
            messages.warning(
                request,
                "🔒 Этот пост доступен только по подписке. Оформите премиум доступ для просмотра.",
            )

    # Увеличиваем счетчик просмотров только при наличии доступа
    if has_access:
        post.increment_views()

    comments = post.comments.filter(is_approved=True)
    comment_form = CommentForm()

    if request.method == "POST" and request.user.is_authenticated and has_access:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.is_approved = False  # На модерацию
            comment.save()
            messages.success(request, "💬 Ваш комментарий отправлен на модерацию.")
            return redirect("content:post_detail", slug=post.slug)

    context = {
        "post": post,
        "has_access": has_access,
        "comments": comments,
        "comment_form": comment_form,
    }
    return render(request, "content/post_detail.html", context)


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            try:
                post = form.save(commit=False)
                post.author = request.user

                # Генерируем slug из заголовка
                base_slug = slugify(post.title)
                if not base_slug:
                    base_slug = "post"

                slug = base_slug
                counter = 1

                # Проверяем уникальность slug
                while Post.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                post.slug = slug
                post.save()

                messages.success(request, "✅ Пост успешно создан!")
                return redirect("content:post_detail", slug=post.slug)

            except Exception as e:
                messages.error(request, f"❌ Ошибка при создании поста: {e}")
                print(f"Error creating post: {e}")
        else:
            messages.error(request, "❌ Пожалуйста, исправьте ошибки в форме")
            print(f"Form errors: {form.errors}")
    else:
        form = PostForm()

    return render(request, "content/post_create.html", {"form": form})


@login_required
def post_drafts(request):
    """Список черновиков текущего пользователя"""
    posts = Post.objects.filter(author=request.user, status="draft").order_by(
        "-created_at"
    )

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "post_type": "Черновики",
        "post_type_icon": "fa-pencil-alt",
        "post_type_color": "warning",
        "empty_message": "У вас пока нет черновиков. Создайте новый пост!",
    }
    return render(request, "content/post_status_list.html", context)


@login_required
def post_archived(request):
    """Список архивных постов текущего пользователя"""
    posts = Post.objects.filter(author=request.user, status="archived").order_by(
        "-updated_at"
    )

    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "post_type": "Архив",
        "post_type_icon": "fa-archive",
        "post_type_color": "secondary",
        "empty_message": "В архиве пока нет постов.",
    }
    return render(request, "content/post_status_list.html", context)


@login_required
def post_archive(request, slug):
    """Отправка поста в архив"""
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if post.status == "archived":
        messages.info(request, "Пост уже находится в архиве.")
    else:
        post.status = "archived"
        post.save()
        messages.success(request, f'Пост "{post.title}" отправлен в архив.')

    return redirect("content:post_archived")


@login_required
def post_publish(request, slug):
    """Публикация черновика"""
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if post.status == "published":
        messages.info(request, "Пост уже опубликован.")
    else:
        post.status = "published"
        post.published_at = timezone.now()
        post.save()
        messages.success(request, f'Пост "{post.title}" опубликован!')

    return redirect("content:post_detail", slug=post.slug)


@login_required
def post_update(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            updated_post = form.save(commit=False)

            # Проверяем, изменился ли заголовок
            if (
                updated_post.title != post.title
            ):  # Используем post.title, а не title_original
                from django.utils.text import slugify

                # Генерируем новый slug из нового заголовка
                base_slug = slugify(updated_post.title)
                new_slug = base_slug
                counter = 1

                # Проверяем уникальность нового slug
                while Post.objects.filter(slug=new_slug).exclude(id=post.id).exists():
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1

                updated_post.slug = new_slug

            updated_post.save()
            messages.success(request, "Пост успешно обновлен!")
            return redirect("content:post_detail", slug=updated_post.slug)
    else:
        form = PostForm(instance=post)

    return render(request, "content/post_update.html", {"form": form, "post": post})


# API Viewsets
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status="published")
    serializer_class = PostSerializer
    lookup_field = "slug"

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category", None)
        is_paid = self.request.query_params.get("is_paid", None)

        if category:
            queryset = queryset.filter(category__slug=category)

        if is_paid is not None:
            queryset = queryset.filter(is_paid=is_paid.lower() == "true")

        return queryset

    @action(detail=True, methods=["post"])
    def comment(self, request, slug=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(post=post, user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = "slug"
