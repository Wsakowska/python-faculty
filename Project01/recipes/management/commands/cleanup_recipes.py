"""
Management command: Usuwanie nieopublikowanych i starych przepisów.

Użycie:
    python manage.py cleanup_recipes              (usuń nieopublikowane starsze niż 30 dni)
    python manage.py cleanup_recipes --days 7     (zmień próg na 7 dni)
    python manage.py cleanup_recipes --dry-run    (podgląd bez usuwania)
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from recipes.models import Recipe


class Command(BaseCommand):
    help = 'Usuwanie nieopublikowanych przepisów starszych niż podana liczba dni.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Usuń nieopublikowane przepisy starsze niż X dni (domyślnie: 30)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Podgląd — pokaż co zostałoby usunięte, ale nie usuwaj',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)

        old_recipes = Recipe.objects.filter(
            is_published=False,
            created_at__lt=cutoff_date,
        )

        count = old_recipes.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS(
                f'Brak nieopublikowanych przepisów starszych niż {days} dni.'
            ))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(f'[DRY RUN] Znaleziono {count} przepisów do usunięcia:'))
            for recipe in old_recipes:
                self.stdout.write(f'  - "{recipe.title}" (autor: {recipe.author}, utworzono: {recipe.created_at:%d.%m.%Y})')
        else:
            old_recipes.delete()
            self.stdout.write(self.style.SUCCESS(
                f'Usunięto {count} nieopublikowanych przepisów starszych niż {days} dni.'
            ))