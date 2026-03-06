from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class UserRegistrationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=17,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Enter phone number (e.g., +1234567890)",
            }
        ),
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter email (optional)"}
        ),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter password"}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm password"}
        )
    )

    class Meta:
        model = User
        fields = ("phone_number", "email", "password1", "password2")


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        max_length=17,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter phone number"}
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter password"}
        )
    )
