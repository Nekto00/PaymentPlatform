from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # Template views
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    # API endpoints
    path("api/register/", views.api_register, name="api_register"),
    path("api/login/", views.api_login, name="api_login"),
    path("api/profile/", views.api_profile, name="api_profile"),
]
