from django import forms

from .models import Category, Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content", "excerpt", "category", "is_paid", "status"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Введите заголовок поста",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 10,
                    "placeholder": "Введите содержание поста",
                }
            ),
            "excerpt": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Краткое описание (необязательно)",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "is_paid": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "status": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {
            "title": "Заголовок",
            "content": "Содержание",
            "excerpt": "Краткое описание",
            "category": "Категория",
            "is_paid": "Только по подписке",
            "status": "Статус",
        }
        help_texts = {
            "is_paid": "Если отмечено, пост будет доступен только пользователям с премиум подпиской",
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Напишите ваш комментарий...",
                }
            )
        }


class PostSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Поиск постов..."}
        ),
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Все категории",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    is_paid = forms.ChoiceField(
        choices=[("", "Все"), ("paid", "По подписке"), ("free", "Бесплатные")],
        required=False,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
