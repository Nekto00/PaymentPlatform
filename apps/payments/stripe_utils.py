import stripe
from django.conf import settings
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(user, price_id=None):
    """
    Create a Stripe Checkout Session for subscription payment
    """
    try:
        price_id = price_id or settings.STRIPE_PRICE_ID

        # Создаем сессию checkout в Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": price_id,
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=settings.BASE_URL
            + reverse("payments:success")
            + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.BASE_URL + reverse("payments:cancel"),
            client_reference_id=user.id,
            customer_email=user.email if user.email else None,
            metadata={
                "user_id": user.id,
                "phone_number": user.phone_number,
            },
        )

        print(f"✅ Stripe сессия создана: {checkout_session.id}")
        print(f"🔗 URL для оплаты: {checkout_session.url}")

        return checkout_session

    except stripe.error.StripeError as e:
        print(f"❌ Stripe ошибка: {e}")
        return None
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        return None
