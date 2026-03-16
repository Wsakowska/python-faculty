"""
Management command: Seedowanie bazy danych przepisami z pliku JSON.

Użycie:
    python manage.py seed_data
    python manage.py seed_data --clear  (wyczyść bazę przed importem)
"""

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from recipes.models import Category, Ingredient, Recipe, RecipeIngredient
from accounts.models import DietaryPreference


class Command(BaseCommand):
    help = 'Seedowanie bazy danych przepisami, składnikami i kategoriami z pliku JSON.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Wyczyść istniejące dane przed importem',
        )

    def handle(self, *args, **options):
        data_file = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'seed_data.json'

        if not data_file.exists():
            self.stderr.write(self.style.ERROR(f'Nie znaleziono pliku: {data_file}'))
            return

        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if options['clear']:
            self.stdout.write('Czyszczenie bazy danych...')
            RecipeIngredient.objects.all().delete()
            Recipe.objects.all().delete()
            Ingredient.objects.all().delete()
            Category.objects.all().delete()
            DietaryPreference.objects.all().delete()
            self.stdout.write(self.style.WARNING('Baza wyczyszczona.'))

        # Utwórz lub pobierz użytkownika do przypisania przepisów
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'is_staff': True, 'is_superuser': True},
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.WARNING(
                'Utworzono konto admin (login: admin, hasło: admin123)'
            ))

        # Import kategorii
        cat_count = 0
        for cat_data in data.get('categories', []):
            obj, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data.get('description', '')},
            )
            if created:
                cat_count += 1
        self.stdout.write(f'Kategorie: dodano {cat_count} nowych.')

        # Import preferencji dietetycznych
        pref_count = 0
        for pref_name in data.get('dietary_preferences', []):
            _, created = DietaryPreference.objects.get_or_create(name=pref_name)
            if created:
                pref_count += 1
        self.stdout.write(f'Preferencje dietetyczne: dodano {pref_count} nowych.')

        # Import składników z pliku CSV (jeśli istnieje)
        csv_file = data_file.parent / 'ingredients.csv'
        ing_count = 0
        if csv_file.exists():
            import csv
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    _, created = Ingredient.objects.get_or_create(
                        name=row['name'],
                        defaults={'unit': row['unit']},
                    )
                    if created:
                        ing_count += 1
            self.stdout.write(f'Składniki z CSV: dodano {ing_count} nowych.')

        # Import przepisów
        recipe_count = 0
        for recipe_data in data.get('recipes', []):
            # Sprawdź czy przepis już istnieje
            if Recipe.objects.filter(title=recipe_data['title']).exists():
                continue

            category = Category.objects.filter(
                name=recipe_data['category']
            ).first()

            recipe = Recipe.objects.create(
                title=recipe_data['title'],
                description=recipe_data['description'],
                instructions=recipe_data['instructions'],
                author=admin_user,
                category=category,
                prep_time=recipe_data['prep_time'],
                difficulty=recipe_data['difficulty'],
            )

            # Dodaj składniki do przepisu
            for ing_data in recipe_data.get('ingredients', []):
                ingredient, _ = Ingredient.objects.get_or_create(
                    name=ing_data['name'],
                )
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ing_data['amount'],
                )

            recipe_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\nSeedowanie zakończone! Dodano {recipe_count} przepisów.'
        ))
