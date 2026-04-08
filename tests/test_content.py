import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.content.models import Post

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestContentModels:
    """Тесты моделей контента"""

    def test_category_creation(self, category):
        assert category.name == "Тестовая категория"
        assert category.slug == "test-category"

    def test_post_creation(self, post, user, category):
        assert post.title == "Тестовый пост"
        assert post.author == user
        assert post.category == category
        assert post.status == "published"
        assert post.views_count == 0

    def test_post_increment_views(self, post):
        initial_views = post.views_count
        post.increment_views()
        post.refresh_from_db()
        assert post.views_count == initial_views + 1


class TestContentViews:
    """Тесты представлений контента"""

    def test_post_list_view(self, client, post):
        url = reverse("content:post_list")
        response = client.get(url)
        assert response.status_code == 200

    def test_post_detail_view(self, client, post):
        url = reverse("content:post_detail", args=[post.slug])
        response = client.get(url)
        assert response.status_code == 200

    def test_post_create_view_authenticated(self, client, user, category):
        client.force_login(user)
        url = reverse("content:post_create")
        response = client.get(url)
        assert response.status_code == 200

    def test_post_create_view_post(self, client, user, category):
        client.force_login(user)
        url = reverse("content:post_create")
        data = {
            "title": "Новый пост",
            "content": "Содержание нового поста",
            "category": category.id,
            "is_paid": False,
            "status": "published",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert Post.objects.filter(title="Новый пост").exists()

    def test_post_drafts_view(self, client, user):
        client.force_login(user)
        Post.objects.create(
            title="Черновик", content="Содержание", author=user, status="draft"
        )
        url = reverse("content:post_drafts")
        response = client.get(url)
        assert response.status_code == 200

    def test_post_archive_view(self, client, user, post):
        client.force_login(user)
        url = reverse("content:post_archive", args=[post.slug])
        response = client.get(url)
        assert response.status_code == 302
        post.refresh_from_db()
        assert post.status == "archived"
