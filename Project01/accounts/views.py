"""Widoki aplikacji accounts."""

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, UserProfileForm
from .models import UserProfile


def register_view(request):
    """Rejestracja nowego użytkownika."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Tworzenie profilu dla nowego użytkownika
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Konto zostało utworzone! Witaj!')
            return redirect('recipes:home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """Wyświetlanie i edycja profilu użytkownika."""
    # Utwórz profil jeśli nie istnieje (np. dla superusera)
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil został zaktualizowany!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
    })