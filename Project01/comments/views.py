"""Widoki aplikacji comments."""

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from recipes.models import Recipe
from .forms import CommentForm


@login_required
def add_comment(request, slug):
    """Dodaj komentarz do przepisu."""
    recipe = get_object_or_404(Recipe, slug=slug)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.recipe = recipe
            comment.author = request.user
            comment.save()
            messages.success(request, 'Komentarz dodany!')

    return redirect('recipes:recipe_detail', slug=slug)