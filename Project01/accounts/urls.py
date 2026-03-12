"""URL-e aplikacji accounts."""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('rejestracja/', views.register_view, name='register'),
    path('logowanie/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'
    ), name='login'),
    path('wyloguj/', auth_views.LogoutView.as_view(), name='logout'),
    path('profil/', views.profile_view, name='profile'),
]