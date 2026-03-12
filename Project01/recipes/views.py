"""Widoki aplikacji recipes."""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.db.models import Count
from .models import Recipe, Category
from .forms import RecipeForm, RecipeIngredientFormSet, IngredientSearchForm

def home(request):
    """Strona główna — najnowsze przepisy."""
    latest_recipes = Recipe.objects.filter(is_published=True)[:6]
    categories = Category.objects.all()
    return render(request, 'recipes/home.html', {
        'latest_recipes': latest_recipes,
        'categories': categories,
    })


def recipe_list(request):
    """Lista wszystkich przepisów z filtrowaniem po kategorii."""
    recipes = Recipe.objects.filter(is_published=True)
    categories = Category.objects.all()

    # Filtrowanie po kategorii
    category_slug = request.GET.get('kategoria')
    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        recipes = recipes.filter(category=active_category)

    return render(request, 'recipes/recipe_list.html', {
        'recipes': recipes,
        'categories': categories,
        'active_category': active_category,
    })


def recipe_detail(request, slug):
    """Szczegóły przepisu."""
    recipe = get_object_or_404(Recipe, slug=slug, is_published=True)
    ingredients = recipe.recipe_ingredients.select_related('ingredient').all()
    comments = recipe.comments.select_related('author').all()
    return render(request, 'recipes/recipe_detail.html', {
        'recipe': recipe,
        'ingredients': ingredients,
        'comments': comments,
    })


@login_required
def recipe_create(request):
    """Dodawanie nowego przepisu."""
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        formset = RecipeIngredientFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            formset.instance = recipe
            formset.save()
            messages.success(request, 'Przepis został dodany!')
            return redirect('recipes:recipe_detail', slug=recipe.slug)
    else:
        form = RecipeForm()
        formset = RecipeIngredientFormSet()

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Dodaj przepis',
    })


@login_required
def recipe_edit(request, slug):
    """Edycja przepisu (tylko autor)."""
    recipe = get_object_or_404(Recipe, slug=slug)

    if recipe.author != request.user:
        messages.error(request, 'Nie możesz edytować cudzego przepisu!')
        return redirect('recipes:recipe_detail', slug=slug)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Przepis został zaktualizowany!')
            return redirect('recipes:recipe_detail', slug=recipe.slug)
    else:
        form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSet(instance=recipe)

    return render(request, 'recipes/recipe_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Edytuj przepis',
    })


@login_required
def recipe_delete(request, slug):
    """Usuwanie przepisu (tylko autor)."""
    recipe = get_object_or_404(Recipe, slug=slug)

    if recipe.author != request.user:
        messages.error(request, 'Nie możesz usunąć cudzego przepisu!')
        return redirect('recipes:recipe_detail', slug=slug)

    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'Przepis został usunięty.')
        return redirect('recipes:recipe_list')

    return render(request, 'recipes/recipe_confirm_delete.html', {
        'recipe': recipe,
    })

def recipe_search(request):
    """Wyszukiwanie przepisów po składnikach — główna funkcja aplikacji."""
    form = IngredientSearchForm(request.GET or None)
    recipes = None
    selected_count = 0

    if form.is_valid():
        selected_ingredients = form.cleaned_data['ingredients']
        selected_count = selected_ingredients.count()

        # Znajdź przepisy, które zawierają KTÓRYKOLWIEK z wybranych składników
        # i posortuj wg liczby pasujących składników (najlepsze dopasowanie na górze)
        recipes = (
            Recipe.objects
            .filter(is_published=True, ingredients__in=selected_ingredients)
            .annotate(
                matched=Count('ingredients', filter=models.Q(
                    ingredients__in=selected_ingredients
                )),
                total_ingredients=Count('recipe_ingredients'),
            )
            .order_by('-matched')
            .distinct()
        )

    return render(request, 'recipes/recipe_search.html', {
        'form': form,
        'recipes': recipes,
        'selected_count': selected_count,
})