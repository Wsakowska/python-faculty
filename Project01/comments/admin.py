"""Rejestracja modeli comments w panelu admina."""

from django.contrib import admin
from .models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'recipe', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']