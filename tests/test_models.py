import os
from datetime import timedelta

import django
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from apps.content.models import Category, Comment, Post
from apps.payments.models import Payment

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "payment_platform.settings")
django.setup()

User = get_user_model()


class AccountsModelTests(TestCase):
    """Тесты моделей аккаунтов"""

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+79991234567",
            password="testpass123",
            email="test@example.com",
        )

    def test_user_creation(self):
        """Тест создания пользователя"""
        self.assertEqual(self.user.phone_number, "+79991234567")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertFalse(self.user.has_paid_subscription)
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)

    def test_user_str_method(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.user), "+79991234567")

    def test_user_without_email(self):
        """Тест создания пользователя без email"""
        user = User.objects.create_user(
            phone_number="+79997654321", password="testpass123"
        )
        self.assertIsNone(user.email)

    def test_user_subscription(self):
        """Тест подписки пользователя"""
        self.user.has_paid_subscription = True
        self.user.subscription_expiry = timezone.now() + timedelta(days=30)
        self.user.save()

        self.assertTrue(self.user.has_paid_subscription)
        self.assertIsNotNone(self.user.subscription_expiry)

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        admin = User.objects.create_superuser(
            phone_number="+79991112233", password="admin123"
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)


class ContentModelTests(TestCase):
    """Тесты моделей контента"""

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+79991234567", password="testpass123"
        )
        self.category = Category.objects.create(
            name="Тестовая категория",
            slug="test-category",
            description="Описание категории",
        )
        self.post = Post.objects.create(
            title="Тестовый пост",
            content="Содержание тестового поста",
            author=self.user,
            category=self.category,
            is_paid=False,
            status="published",
        )

    def test_category_creation(self):
        """Тест создания категории"""
        self.assertEqual(self.category.name, "Тестовая категория")
        self.assertEqual(self.category.slug, "test-category")
        self.assertEqual(str(self.category), "Тестовая категория")

    def test_post_creation(self):
        """Тест создания поста"""
        self.assertEqual(self.post.title, "Тестовый пост")
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.category, self.category)
        self.assertFalse(self.post.is_paid)
        self.assertEqual(self.post.status, "published")
        self.assertEqual(self.post.views_count, 0)

    def test_post_str_method(self):
        """Тест строкового представления поста"""
        self.assertEqual(str(self.post), "Тестовый пост")

    def test_post_increment_views(self):
        """Тест увеличения просмотров"""
        initial_views = self.post.views_count
        self.post.increment_views()
        self.post.refresh_from_db()
        self.assertEqual(self.post.views_count, initial_views + 1)

    def test_post_published_at(self):
        """Тест даты публикации"""
        post = Post.objects.create(
            title="Пост для проверки даты",
            content="Содержание",
            author=self.user,
            status="published",
        )
        self.assertIsNotNone(post.published_at)

    def test_post_draft(self):
        """Тест черновика"""
        post = Post.objects.create(
            title="Черновик", content="Содержание", author=self.user, status="draft"
        )
        self.assertIsNone(post.published_at)

    def test_comment_creation(self):
        """Тест создания комментария"""
        comment = Comment.objects.create(
            post=self.post, user=self.user, content="Тестовый комментарий"
        )
        self.assertEqual(comment.content, "Тестовый комментарий")
        self.assertFalse(comment.is_approved)
        self.assertEqual(
            str(comment),
            f"Комментарий от {self.user.phone_number} к посту {self.post.title}",
        )


class PaymentModelTests(TestCase):
    """Тесты моделей платежей"""

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="+79991234567", password="testpass123"
        )

    def test_payment_creation(self):
        """Тест создания платежа"""
        payment = Payment.objects.create(
            user=self.user,
            stripe_payment_intent_id="pi_test_123",
            amount=29.99,
            currency="usd",
            status="succeeded",
        )
        self.assertEqual(payment.amount, 29.99)
        self.assertEqual(payment.status, "succeeded")
        self.assertEqual(str(payment), "Платеж pi_test_123 - Успешно")

    def test_payment_status_choices(self):
        """Тест статусов платежа"""
        payment = Payment.objects.create(
            user=self.user,
            stripe_payment_intent_id="pi_test_456",
            amount=29.99,
            currency="usd",
            status="pending",
        )
        self.assertEqual(payment.status, "pending")

        payment.status = "failed"
        payment.save()
        self.assertEqual(payment.status, "failed")
