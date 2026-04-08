from datetime import timedelta

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .models import Payment, PostPurchase


@login_required
def create_subscription(request):
    """Создание подписки - перенаправление на Stripe Checkout"""
    # Проверяем текущую подписку
    if request.user.has_paid_subscription:
        if (
            request.user.subscription_expiry
            and request.user.subscription_expiry > timezone.now()
        ):
            messages.info(
                request,
                f'У вас уже есть активная подписка до {request.user.subscription_expiry.strftime("%d.%m.%Y")}',
            )
            return redirect("content:post_list")
        else:
            request.user.has_paid_subscription = False
            request.user.save()

    # Проверяем наличие Stripe ключей
    if not settings.STRIPE_SECRET_KEY or not settings.STRIPE_PUBLISHABLE_KEY:
        print("❌ Stripe ключи не найдены!")

        # ВРЕМЕННО: тестовый режим без Stripe
        if settings.DEBUG:
            messages.warning(
                request, "Режим разработки: подписка активирована без оплаты"
            )
            request.user.has_paid_subscription = True
            request.user.subscription_expiry = timezone.now() + timedelta(days=30)
            request.user.save()
            return redirect("payments:success")
        else:
            messages.error(
                request,
                "Платежная система не настроена. Пожалуйста, свяжитесь с администратором.",
            )
            return redirect("content:post_list")

    try:
        # Устанавливаем ключ Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        # Создаем сессию в Stripe
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price": settings.STRIPE_PRICE_ID,
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=settings.BASE_URL
            + "/payments/success/?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=settings.BASE_URL + "/payments/cancel/",
            client_reference_id=request.user.id,
            customer_email=request.user.email if request.user.email else None,
            metadata={
                "user_id": request.user.id,
                "phone_number": request.user.phone_number,
            },
        )

        print(f"✅ Stripe сессия создана: {checkout_session.id}")
        print(f"🔗 URL для оплаты: {checkout_session.url}")

        return redirect(checkout_session.url)

    except Exception as e:
        print(f"❌ Ошибка при создании подписки: {e}")

        # ВРЕМЕННО: при ошибке активируем тестовую подписку
        if settings.DEBUG:
            messages.warning(
                request,
                f"Режим разработки: подписка активирована (ошибка: {str(e)[:50]}...)",
            )
            request.user.has_paid_subscription = True
            request.user.subscription_expiry = timezone.now() + timedelta(days=30)
            request.user.save()
            return redirect("payments:success")
        else:
            messages.error(request, "Произошла ошибка при обработке запроса.")
            return redirect("content:post_list")


@login_required
def payment_success(request):
    """Страница успешной оплаты"""
    session_id = request.GET.get("session_id")

    if session_id:
        try:
            # Получаем информацию о сессии из Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            session = stripe.checkout.Session.retrieve(session_id)

            # Проверяем статус платежа
            if session.payment_status == "paid":
                # Активируем подписку пользователя
                from datetime import timedelta

                from django.utils import timezone

                request.user.has_paid_subscription = True
                request.user.subscription_expiry = timezone.now() + timedelta(days=30)
                request.user.save()

                # Создаем запись о платеже
                Payment.objects.create(
                    user=request.user,
                    stripe_payment_intent_id=session.payment_intent,
                    amount=session.amount_total / 100,
                    currency=session.currency,
                    status="succeeded",
                )

                messages.success(
                    request, "✅ Оплата прошла успешно! Подписка активирована."
                )
            else:
                messages.warning(
                    request,
                    "Платеж обрабатывается. Вы получите уведомление после подтверждения.",
                )

        except Exception as e:
            print(f"❌ Ошибка при проверке платежа: {e}")
            messages.error(
                request,
                "Не удалось подтвердить оплату. Если средства списаны, обратитесь в поддержку.",
            )

    return render(request, "payments/success.html")


@login_required
def purchase_post(request, post_id, get_object_or_404=None):
    from apps.content.models import Post

    post = get_object_or_404(Post, id=post_id, is_paid=True)

    # Проверяем, не купил ли уже
    if PostPurchase.objects.filter(user=request.user, post=post).exists():
        messages.info(request, "Вы уже купили этот пост")
        return redirect("content:post_detail", slug=post.slug)

    try:
        # Создаем платеж в Stripe
        import stripe

        stripe.api_key = settings.STRIPE_SECRET_KEY

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(post.price * 100),
                        "product_data": {
                            "name": post.title,
                            "description": post.excerpt[:100],
                        },
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url=settings.BASE_URL
            + f"/payments/post-purchase-success/?post_id={post.id}&session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=settings.BASE_URL + f"/content/post/{post.slug}/",
            client_reference_id=request.user.id,
            metadata={
                "user_id": request.user.id,
                "post_id": post.id,
                "post_title": post.title,
                "type": "post_purchase",
            },
        )

        return redirect(checkout_session.url)

    except Exception as e:
        messages.error(request, f"Ошибка при создании платежа: {e}")
        return redirect("content:post_detail", slug=post.slug)


@login_required
def payment_cancel(request):
    """Страница отмены оплаты"""
    messages.warning(
        request,
        "Вы отменили процесс оплаты. Попробуйте снова, если хотите оформить подписку.",
    )
    return redirect("content:post_list")


@login_required
def payment_history(request):
    """История платежей"""
    payments = Payment.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "payments/history.html", {"payments": payments})


@csrf_exempt
def stripe_webhook(request):
    """Обработка вебхуков от Stripe"""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # Обработка успешного платежа
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        # Здесь можно активировать подписку (на всякий случай, если success page не сработал)
        from datetime import timedelta

        from django.utils import timezone

        from apps.accounts.models import User
        from apps.payments.models import Payment

        try:
            user = User.objects.get(id=session["client_reference_id"])

            # Проверяем, не активирована ли уже подписка
            if not user.has_paid_subscription:
                user.has_paid_subscription = True
                user.subscription_expiry = timezone.now() + timedelta(days=30)
                user.save()

            # Создаем запись о платеже
            Payment.objects.get_or_create(
                stripe_payment_intent_id=session["payment_intent"],
                defaults={
                    "user": user,
                    "amount": session["amount_total"] / 100,
                    "currency": session["currency"],
                    "status": "succeeded",
                },
            )

            print(
                f"✅ Вебхук: подписка активирована для пользователя {user.phone_number}"
            )

        except User.DoesNotExist:
            print("❌ Вебхук: пользователь не найден")

    return HttpResponse(status=200)
