"""Serializery REST API."""

from rest_framework import serializers
from django.contrib.auth.models import User
from recipes.models import Category, Ingredient, Recipe, RecipeIngredient
from accounts.models import DietaryPreference
from comments.models import Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']


class IngredientSerializer(serializers.ModelSerializer):
    unit_display = serializers.CharField(source='get_unit_display', read_only=True)

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'unit', 'unit_display']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient_name = serializers.CharField(source='ingredient.name', read_only=True)
    unit = serializers.CharField(source='ingredient.unit', read_only=True)
    unit_display = serializers.CharField(source='ingredient.get_unit_display', read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'ingredient', 'ingredient_name', 'amount', 'unit', 'unit_display']


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'author_name', 'content', 'rating', 'created_at']
        read_only_fields = ['author']


class RecipeListSerializer(serializers.ModelSerializer):
    """Skrócony serializer do listy przepisów."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'slug', 'description', 'author_name',
                  'category', 'category_name', 'prep_time', 'difficulty',
                  'difficulty_display', 'is_published', 'created_at',
                  'comments_count']


class RecipeDetailSerializer(serializers.ModelSerializer):
    """Pełny serializer z składnikami i komentarzami."""
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    recipe_ingredients = RecipeIngredientSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    dietary_preferences = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'slug', 'description', 'instructions',
                  'author', 'author_name', 'category', 'category_name',
                  'prep_time', 'difficulty', 'difficulty_display',
                  'dietary_preferences', 'is_published', 'created_at',
                  'updated_at', 'recipe_ingredients', 'comments']


class DietaryPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietaryPreference
        fields = ['id', 'name']


class SearchResultSerializer(serializers.ModelSerializer):
    """Serializer wyników wyszukiwania z dopasowaniem."""
    matched = serializers.IntegerField(read_only=True)
    total_ingredients = serializers.IntegerField(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'slug', 'description', 'category_name',
                  'prep_time', 'difficulty_display', 'matched', 'total_ingredients']