import os
from datetime import timedelta

import django
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.content.models import Category, Post

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "payment_platform.settings")
django.setup()

User = get_user_model()


class AccountsViewsTests(TestCase):
    """Тесты представлений аккаунтов"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            phone_number="+79991234567",
            password="testpass123",
            email="test@example.com",
        )
        self.register_url = reverse("accounts:register")
        self.login_url = reverse("accounts:login")
        self.profile_url = reverse("accounts:profile")
        self.logout_url = reverse("accounts:logout")

    def test_register_view_get(self):
        """Тест GET запроса на регистрацию"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_view_post(self):
        """Тест POST запроса на регистрацию"""
        response = self.client.post(
            self.register_url,
            {
                "phone_number": "+79997654321",
                "password1": "newpass123",
                "password2": "newpass123",
                "email": "new@example.com",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect после регистрации
        self.assertTrue(User.objects.filter(phone_number="+79997654321").exists())

    def test_login_view_get(self):
        """Тест GET запроса на вход"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_view_post(self):
        """Тест POST запроса на вход"""
        response = self.client.post(
            self.login_url, {"username": "+79991234567", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 302)  # Redirect после входа

    def test_profile_view_authenticated(self):
        """Тест профиля для авторизованного пользователя"""
        self.client.login(phone_number="+79991234567", password="testpass123")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")

    def test_profile_view_unauthenticated(self):
        """Тест профиля для неавторизованного пользователя"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)  # Redirect на login

    def test_logout_view(self):
        """Тест выхода"""
        self.client.login(phone_number="+79991234567", password="testpass123")
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)  # Redirect после выхода


class ContentViewsTests(TestCase):
    """Тесты представлений контента"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            phone_number="+79991234567", password="testpass123"
        )
        self.category = Category.objects.create(
            name="Тестовая категория", slug="test-category"
        )
        self.post = Post.objects.create(
            title="Тестовый пост",
            content="Содержание тестового поста",
            author=self.user,
            category=self.category,
            status="published",
        )
        self.post_list_url = reverse("content:post_list")
        self.post_detail_url = reverse("content:post_detail", args=[self.post.slug])
        self.post_create_url = reverse("content:post_create")
        self.post_drafts_url = reverse("content:post_drafts")
        self.post_archived_url = reverse("content:post_archived")

    def test_post_list_view(self):
        """Тест списка постов"""
        response = self.client.get(self.post_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "content/post_list.html")
        self.assertContains(response, "Тестовый пост")

    def test_post_detail_view(self):
        """Тест детального просмотра поста"""
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "content/post_detail.html")
        self.assertContains(response, "Тестовый пост")

    def test_post_detail_view_increment_views(self):
        """Тест увеличения просмотров"""
        initial_views = self.post.views_count
        self.client.get(self.post_detail_url)
        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, initial_views + 1)

    def test_post_create_view_get(self):
        """Тест GET запроса на создание поста"""
        self.client.login(phone_number="+79991234567", password="testpass123")
        response = self.client.get(self.post_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "content/post_create.html")

    def test_post_create_view_post(self):
        """Тест POST запроса на создание поста"""
        self.client.login(phone_number="+79991234567", password="testpass123")
        response = self.client.post(
            self.post_create_url,
            {
                "title": "Новый пост",
                "content": "Содержание нового поста",
                "category": self.category.id,
                "is_paid": False,
                "status": "published",
            },
        )
        self.assertEqual(response.status_code, 302)  # Redirect после создания
        self.assertTrue(Post.objects.filter(title="Новый пост").exists())

    def test_post_drafts_view(self):
        """Тест черновиков"""
        self.client.login(phone_number="+79991234567", password="testpass123")
        Post.objects.create(
            title="Черновик", content="Содержание", author=self.user, status="draft"
        )
        response = self.client.get(self.post_drafts_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "content/post_status_list.html")
        self.assertContains(response, "Черновик")

    def test_post_archive_view(self):
        """Тест архивации поста"""
        self.client.login(phone_number="+79991234567", password="testpass123")
        archive_url = reverse("content:post_archive", args=[self.post.slug])
        response = self.client.get(archive_url)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.post.refresh_from_db()
        self.assertEqual(self.post.status, "archived")

    def test_paid_post_without_subscription(self):
        """Тест платного поста без подписки"""
        paid_post = Post.objects.create(
            title="Платный пост",
            content="Содержание",
            author=self.user,
            is_paid=True,
            status="published",
        )
        url = reverse("content:post_detail", args=[paid_post.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "только по подписке")

    def test_paid_post_with_subscription(self):
        """Тест платного поста с подпиской"""
        self.user.has_paid_subscription = True
        self.user.save()
        self.client.login(phone_number="+79991234567", password="testpass123")

        paid_post = Post.objects.create(
            title="Платный пост",
            content="Содержание",
            author=self.user,
            is_paid=True,
            status="published",
        )
        url = reverse("content:post_detail", args=[paid_post.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, paid_post.content)


class PaymentViewsTests(TestCase):
    """Тесты представлений платежей"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            phone_number="+79991234567", password="testpass123"
        )
        self.create_url = reverse("payments:create")
        self.success_url = reverse("payments:success")
        self.cancel_url = reverse("payments:cancel")
        self.history_url = reverse("payments:history")

    def test_create_subscription_authenticated(self):
        """Тест создания подписки авторизованным пользователем"""
        self.client.login(phone_number="+79991234567", password="testpass123")
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_create_subscription_unauthenticated(self):
        """Тест создания подписки неавторизованным пользователем"""
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)  # Redirect на login

    def test_payment_success_view(self):
        """Тест страницы успешной оплаты"""
        self.client.login(phone_number="+79991234567", password="testpass123")
        response = self.client.get(self.success_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payments/success.html")

    def test_payment_cancel_view(self):
        """Тест страницы отмены оплаты"""
        self.client.login(phone_number="+79991234567", password="testpass123")
        response = self.client.get(self.cancel_url)
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_user_with_active_subscription(self):
        """Тест пользователя с активной подпиской"""
        self.user.has_paid_subscription = True
        self.user.subscription_expiry = timezone.now() + timedelta(days=30)
        self.user.save()
        self.client.login(phone_number="+79991234567", password="testpass123")

        response = self.client.get(self.create_url)
        self.assertEqual(
            response.status_code, 302
        )  # Redirect с сообщением о существующей подписке
