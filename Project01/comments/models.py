"""Modele aplikacji comments."""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Comment(models.Model):
    """Komentarz z oceną pod przepisem."""
    recipe = models.ForeignKey(
        'recipes.Recipe', on_delete=models.CASCADE,
        related_name='comments', verbose_name='przepis'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments', verbose_name='autor'
    )
    content = models.TextField('treść')
    rating = models.IntegerField(
        'ocena',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Ocena od 1 do 5'
    )
    created_at = models.DateTimeField('data utworzenia', auto_now_add=True)

    class Meta:
        verbose_name = 'komentarz'
        verbose_name_plural = 'komentarze'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.author.username} — {self.recipe.title} ({self.rating}/5)"