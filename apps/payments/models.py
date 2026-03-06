from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Payment(models.Model):
    PAYMENT_STATUS = (
        ("pending", "Ожидание"),
        ("succeeded", "Успешно"),
        ("failed", "Ошибка"),
        ("refunded", "Возврат"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    stripe_payment_intent_id = models.CharField(
        max_length=255, unique=True, verbose_name="ID платежа"
    )
    stripe_customer_id = models.CharField(
        max_length=255, blank=True, verbose_name="ID клиента"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    currency = models.CharField(max_length=3, default="usd", verbose_name="Валюта")
    status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS, default="pending", verbose_name="Статус"
    )
    description = models.CharField(max_length=255, blank=True, verbose_name="Описание")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Метаданные")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Платеж {self.stripe_payment_intent_id} - {self.get_status_display()}"


class PostPurchase(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_purchases"
    )
    post = models.ForeignKey(
        "content.Post", on_delete=models.CASCADE, related_name="purchases"
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, related_name="post_purchases"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "user",
            "post",
        ]  # Один пользователь может купить пост только один раз
        verbose_name = "Покупка поста"
        verbose_name_plural = "Покупки постов"
