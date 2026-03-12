"""Modele aplikacji accounts."""

from django.db import models
from django.contrib.auth.models import User


class DietaryPreference(models.Model):
    """Preferencja dietetyczna, np. Wegetariańskie, Bezglutenowe."""
    name = models.CharField('nazwa', max_length=100, unique=True)

    class Meta:
        verbose_name = 'preferencja dietetyczna'
        verbose_name_plural = 'preferencje dietetyczne'
        ordering = ['name']

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    """Profil użytkownika z preferencjami i ulubionymi przepisami."""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='profile', verbose_name='użytkownik'
    )
    bio = models.TextField('o mnie', blank=True)
    dietary_preferences = models.ManyToManyField(
        DietaryPreference, blank=True,
        related_name='users', verbose_name='preferencje dietetyczne'
    )
    favorite_recipes = models.ManyToManyField(
        'recipes.Recipe', blank=True,
        related_name='favorited_by', verbose_name='ulubione przepisy'
    )

    class Meta:
        verbose_name = 'profil użytkownika'
        verbose_name_plural = 'profile użytkowników'

    def __str__(self):
        return f"Profil: {self.user.username}"