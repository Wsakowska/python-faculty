"""Widoki aplikacji recipes."""

from django.shortcuts import render


def home(request):
    """Strona główna."""
    return render(request, 'recipes/home.html')