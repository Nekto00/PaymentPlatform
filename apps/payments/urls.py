from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("create/", views.create_subscription, name="create"),
    path("success/", views.payment_success, name="success"),
    path("cancel/", views.payment_cancel, name="cancel"),
    path("history/", views.payment_history, name="history"),
    path("webhook/", views.stripe_webhook, name="webhook"),
    path("purchase/post/<int:post_id>/", views.purchase_post, name="purchase_post"),
]
