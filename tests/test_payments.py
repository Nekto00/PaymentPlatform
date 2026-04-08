from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from apps.payments.models import Payment

User = get_user_model()

pytestmark = pytest.mark.django_db


class TestPaymentModels:
    """Тесты моделей платежей"""

    def test_payment_creation(self, user):
        payment = Payment.objects.create(
            user=user,
            stripe_payment_intent_id="pi_test_123",
            amount=29.99,
            currency="usd",
            status="succeeded",
        )
        assert payment.amount == 29.99
        assert payment.status == "succeeded"
        assert str(payment) == "Платеж pi_test_123 - Успешно"


class TestPaymentViews:
    """Тесты представлений платежей"""

    def test_create_subscription_unauthenticated(self, client):
        url = reverse("payments:create")
        response = client.get(url)
        assert response.status_code == 302  # Redirect на login

    def test_create_subscription_authenticated(self, client, user):
        client.force_login(user)

        with patch("apps.payments.views.create_checkout_session") as mock_create:
            mock_session = MagicMock()
            mock_session.url = "/payments/success/"
            mock_create.return_value = mock_session

            url = reverse("payments:create")
            response = client.get(url)
            assert response.status_code == 302

    def test_payment_success_view(self, client, user):
        client.force_login(user)
        url = reverse("payments:success")
        response = client.get(url)
        assert response.status_code == 200

    def test_payment_cancel_view(self, client, user):
        client.force_login(user)
        url = reverse("payments:cancel")
        response = client.get(url)
        assert response.status_code == 302

    def test_payment_history_view(self, client, user):
        client.force_login(user)
        Payment.objects.create(
            user=user,
            stripe_payment_intent_id="pi_test_unique_123",
            amount=29.99,
            currency="usd",
            status="succeeded",
        )
        url = reverse("payments:history")
        response = client.get(url)
        assert response.status_code == 200

    def test_user_with_active_subscription(self, client, user):
        user.has_paid_subscription = True
        user.subscription_expiry = timezone.now() + timedelta(days=30)
        user.save()
        client.force_login(user)

        url = reverse("payments:create")
        response = client.get(url)
        assert response.status_code == 302
