"""Rejestracja modeli accounts w panelu admina."""

from django.contrib import admin
from .models import DietaryPreference, UserProfile


@admin.register(DietaryPreference)
class DietaryPreferenceAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user']