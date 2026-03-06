# tests/test_accounts.py
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestAccountsViews:
    """Тесты представлений аккаунтов"""

    def test_register_view_get(self, client):
        url = reverse("accounts:register")
        response = client.get(url)
        assert response.status_code == 200

    def test_register_view_post(self, client):
        url = reverse("accounts:register")
        data = {
            "phone_number": "+79997654321",
            "password1": "testpass123",
            "password2": "testpass123",
            "email": "new@example.com",
        }
        response = client.post(url, data)
        assert response.status_code == 302
        assert User.objects.filter(phone_number="+79997654321").exists()

    def test_login_view_get(self, client):
        url = reverse("accounts:login")
        response = client.get(url)
        assert response.status_code == 200

    def test_login_view_post(self, client, user):
        url = reverse("accounts:login")
        data = {"username": user.phone_number, "password": "testpass123"}
        response = client.post(url, data)
        assert response.status_code == 302

    def test_profile_view_authenticated(self, client, user):
        client.force_login(user)
        url = reverse("accounts:profile")
        response = client.get(url)
        assert response.status_code == 200

    def test_profile_view_unauthenticated(self, client):
        url = reverse("accounts:profile")
        response = client.get(url)
        assert response.status_code == 302


class TestAccountsAPI:
    """Тесты API аккаунтов"""

    def test_api_register(self, api_client):
        url = reverse("accounts:api_register")
        data = {
            "phone_number": "+79997654321",
            "password": "testpass123",
            "email": "new@example.com",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "access" in response.data

    def test_api_login(self, api_client, user):
        url = reverse("accounts:api_login")
        data = {"phone_number": user.phone_number, "password": "testpass123"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_api_profile_authenticated(self, api_client, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

        url = reverse("accounts:api_profile")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["phone_number"] == user.phone_number
