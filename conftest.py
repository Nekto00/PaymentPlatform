import os
import django
import pytest

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payment_platform.test_settings')
django.setup()

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user():
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        phone_number='+79991234567',
        password='testpass123',
        email='test@example.com'
    )

@pytest.fixture
def category():
    from apps.content.models import Category
    return Category.objects.create(
        name='Тестовая категория',
        slug='test-category'
    )

@pytest.fixture
def post(user, category):
    from apps.content.models import Post
    return Post.objects.create(
        title='Тестовый пост',
        content='Содержание тестового поста',
        author=user,
        category=category,
        status='published'
    )
