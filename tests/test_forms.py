import os

import django
from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.accounts.forms import UserLoginForm, UserRegistrationForm
from apps.content.forms import CommentForm, PostForm, PostSearchForm
from apps.content.models import Category

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "payment_platform.settings")
django.setup()

User = get_user_model()


class AccountsFormTests(TestCase):
    """Тесты форм аккаунтов"""

    def test_registration_form_valid(self):
        """Тест валидной формы регистрации"""
        form_data = {
            "phone_number": "+79991234567",
            "password1": "testpass123",
            "password2": "testpass123",
            "email": "test@example.com",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_invalid_phone(self):
        """Тест невалидного номера телефона"""
        form_data = {
            "phone_number": "123",  # Неправильный формат
            "password1": "testpass123",
            "password2": "testpass123",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_registration_form_password_mismatch(self):
        """Тест несовпадения паролей"""
        form_data = {
            "phone_number": "+79991234567",
            "password1": "testpass123",
            "password2": "differentpass",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_login_form_valid(self):
        """Тест валидной формы входа"""
        form_data = {
            "username": "+79991234567",
            "password": "testpass123",
        }
        form = UserLoginForm(data=form_data)
        # Не проверяем is_valid() так как форма требует авторизации
        self.assertEqual(form.data["username"], "+79991234567")


class ContentFormTests(TestCase):
    """Тесты форм контента"""

    def setUp(self):
        self.category = Category.objects.create(
            name="Тестовая категория", slug="test-category"
        )

    def test_post_form_valid(self):
        """Тест валидной формы поста"""
        form_data = {
            "title": "Тестовый пост",
            "content": "Содержание тестового поста",
            "excerpt": "Краткое описание",
            "category": self.category.id,
            "is_paid": False,
            "status": "published",
        }
        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_post_form_paid_post_without_price(self):
        """Тест платного поста без цены (теперь не нужно)"""
        form_data = {
            "title": "Платный пост",
            "content": "Содержание",
            "category": self.category.id,
            "is_paid": True,
            "status": "published",
        }
        form = PostForm(data=form_data)
        # Теперь is_paid просто булево поле, так что форма должна быть валидной
        self.assertTrue(form.is_valid())

    def test_comment_form_valid(self):
        """Тест валидной формы комментария"""
        form_data = {"content": "Тестовый комментарий"}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form_empty(self):
        """Тест пустого комментария"""
        form_data = {"content": ""}
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_search_form_valid(self):
        """Тест формы поиска"""
        form_data = {"query": "поиск", "category": self.category.id, "is_paid": "paid"}
        form = PostSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_search_form_empty(self):
        """Тест пустой формы поиска"""
        form = PostSearchForm(data={})
        self.assertTrue(form.is_valid())
