"""Modele aplikacji recipes."""

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    """Kategoria przepisu, np. Śniadanie, Obiad, Deser."""
    name = models.CharField('nazwa', max_length=100, unique=True)
    slug = models.SlugField('slug', max_length=100, unique=True, blank=True)
    description = models.TextField('opis', blank=True)

    class Meta:
        verbose_name = 'kategoria'
        verbose_name_plural = 'kategorie'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Składnik, np. jajko, mąka, mleko."""
    UNIT_CHOICES = [
        ('szt', 'sztuki'),
        ('g', 'gramy'),
        ('kg', 'kilogramy'),
        ('ml', 'mililitry'),
        ('l', 'litry'),
        ('łyżka', 'łyżki'),
        ('łyżeczka', 'łyżeczki'),
        ('szklanka', 'szklanki'),
        ('szczypta', 'szczypty'),
        ('plaster', 'plastry'),
        ('ząbek', 'ząbki'),
    ]

    name = models.CharField('nazwa', max_length=100, unique=True)
    unit = models.CharField('jednostka', max_length=20, choices=UNIT_CHOICES, default='szt')

    class Meta:
        verbose_name = 'składnik'
        verbose_name_plural = 'składniki'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Przepis kulinarny."""
    DIFFICULTY_CHOICES = [
        ('easy', 'Łatwy'),
        ('medium', 'Średni'),
        ('hard', 'Trudny'),
    ]

    title = models.CharField('tytuł', max_length=200)
    slug = models.SlugField('slug', max_length=200, unique=True, blank=True)
    description = models.TextField('opis')
    instructions = models.TextField('instrukcje przygotowania')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes', verbose_name='autor'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, related_name='recipes', verbose_name='kategoria'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        related_name='recipes', verbose_name='składniki'
    )
    dietary_preferences = models.ManyToManyField(
        'accounts.DietaryPreference', blank=True,
        related_name='recipes', verbose_name='preferencje dietetyczne'
    )
    prep_time = models.PositiveIntegerField('czas przygotowania (min)')
    difficulty = models.CharField(
        'poziom trudności', max_length=10,
        choices=DIFFICULTY_CHOICES, default='medium'
    )
    image = models.ImageField('zdjęcie', upload_to='recipes/', blank=True)
    is_published = models.BooleanField('opublikowany', default=True)
    created_at = models.DateTimeField('data utworzenia', auto_now_add=True)
    updated_at = models.DateTimeField('data modyfikacji', auto_now=True)

    class Meta:
        verbose_name = 'przepis'
        verbose_name_plural = 'przepisy'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class RecipeIngredient(models.Model):
    """Tabela pośrednia — ile jakiego składnika potrzeba do przepisu."""
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_ingredients', verbose_name='przepis'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE,
        related_name='recipe_ingredients', verbose_name='składnik'
    )
    amount = models.DecimalField('ilość', max_digits=7, decimal_places=2)

    class Meta:
        verbose_name = 'składnik przepisu'
        verbose_name_plural = 'składniki przepisu'
        unique_together = ['recipe', 'ingredient']

    def __str__(self):
        return f"{self.amount} {self.ingredient.unit} {self.ingredient.name}"