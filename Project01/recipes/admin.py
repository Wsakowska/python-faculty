"""Rejestracja modeli recipes w panelu admina."""

from django.contrib import admin
from .models import Category, Ingredient, Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    """Składniki wyświetlane inline przy edycji przepisu."""
    model = RecipeIngredient
    extra = 3


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'unit']
    list_filter = ['unit']
    search_fields = ['name']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'difficulty', 'is_published', 'created_at']
    list_filter = ['category', 'difficulty', 'is_published']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [RecipeIngredientInline]