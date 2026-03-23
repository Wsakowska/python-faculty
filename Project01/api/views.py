"""Widoki REST API."""

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from django.db.models import Count, Q

from recipes.models import Category, Ingredient, Recipe
from accounts.models import DietaryPreference
from comments.models import Comment

from .serializers import (
    CategorySerializer, IngredientSerializer,
    RecipeListSerializer, RecipeDetailSerializer,
    DietaryPreferenceSerializer, CommentSerializer,
    SearchResultSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API kategorii przepisów.

    list: Lista wszystkich kategorii.
    retrieve: Szczegóły kategorii.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API składników.

    list: Lista wszystkich składników.
    retrieve: Szczegóły składnika.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API przepisów.

    list: Lista opublikowanych przepisów.
    retrieve: Pełne szczegóły przepisu ze składnikami i komentarzami.
    """
    queryset = Recipe.objects.filter(is_published=True)
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        return RecipeListSerializer

    @action(detail=True, methods=['get'])
    def comments(self, request, slug=None):
        """Lista komentarzy do przepisu."""
        recipe = self.get_object()
        comments = recipe.comments.select_related('author').all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


class DietaryPreferenceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API preferencji dietetycznych.

    list: Lista wszystkich preferencji.
    """
    queryset = DietaryPreference.objects.all()
    serializer_class = DietaryPreferenceSerializer


@api_view(['GET'])
def search_by_ingredients(request):
    """
    Wyszukiwanie przepisów po składnikach.

    Parametry GET:
    - ingredients: lista ID składników (można podać wielokrotnie)

    Przykład: /api/szukaj/?ingredients=1&ingredients=2&ingredients=5

    Zwraca przepisy posortowane wg liczby pasujących składników.
    """
    ingredient_ids = request.GET.getlist('ingredients')

    if not ingredient_ids:
        return Response(
            {'error': 'Podaj przynajmniej jeden składnik. Użyj parametru ?ingredients=ID.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        ingredient_ids = [int(i) for i in ingredient_ids]
    except ValueError:
        return Response(
            {'error': 'ID składników muszą być liczbami.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    recipes = (
        Recipe.objects
        .filter(is_published=True, ingredients__id__in=ingredient_ids)
        .annotate(
            matched=Count('ingredients', filter=Q(ingredients__id__in=ingredient_ids)),
            total_ingredients=Count('recipe_ingredients'),
        )
        .order_by('-matched')
        .distinct()
    )

    serializer = SearchResultSerializer(recipes, many=True)
    return Response({
        'selected_ingredients': ingredient_ids,
        'results_count': recipes.count(),
        'results': serializer.data,
    })