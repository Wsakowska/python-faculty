"""Formularze aplikacji accounts."""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class RegisterForm(UserCreationForm):
    """Formularz rejestracji z dodatkowym polem email."""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UserProfileForm(forms.ModelForm):
    """Formularz edycji profilu użytkownika."""

    class Meta:
        model = UserProfile
        fields = ['bio', 'dietary_preferences']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'dietary_preferences': forms.CheckboxSelectMultiple,
        }