from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdmin(BaseUserAdmin):
    # Поля, отображаемые в списке пользователей
    list_display = (
        "phone_number",
        "email",
        "has_paid_subscription",
        "is_staff",
        "is_active",
    )
    list_filter = ("is_staff", "is_active", "has_paid_subscription")

    # Поля для формы редактирования пользователя
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (_("Personal info"), {"fields": ("email",)}),
        (
            _("Subscription"),
            {"fields": ("has_paid_subscription", "subscription_expiry")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # Поля для формы создания пользователя
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "email", "password1", "password2"),
            },
        ),
    )

    search_fields = ("phone_number", "email")
    ordering = ("phone_number",)
    filter_horizontal = ("groups", "user_permissions")


admin.site.register(User, UserAdmin)
