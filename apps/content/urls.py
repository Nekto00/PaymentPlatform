from django.urls import path

from . import views

app_name = "content"

urlpatterns = [
    # Основные маршруты
    path("", views.post_list, name="post_list"),
    path("drafts/", views.post_drafts, name="post_drafts"),
    path("archived/", views.post_archived, name="post_archived"),
    path("post/create/", views.post_create, name="post_create"),
    path("post/<slug:slug>/", views.post_detail, name="post_detail"),
    path("post/<slug:slug>/edit/", views.post_update, name="post_update"),
    path("post/<slug:slug>/archive/", views.post_archive, name="post_archive"),
    path("post/<slug:slug>/publish/", views.post_publish, name="post_publish"),
]
