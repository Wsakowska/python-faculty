"""
Management command: Import składników z pliku CSV.

Użycie:
    python manage.py import_ingredients
    python manage.py import_ingredients --file inna_sciezka.csv
"""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import składników z pliku CSV (kolumny: name, unit).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default=None,
            help='Ścieżka do pliku CSV (domyślnie: data/ingredients.csv)',
        )

    def handle(self, *args, **options):
        if options['file']:
            csv_path = Path(options['file'])
        else:
            csv_path = Path(__file__).resolve().parent.parent.parent.parent / 'data' / 'ingredients.csv'

        if not csv_path.exists():
            self.stderr.write(self.style.ERROR(f'Nie znaleziono pliku: {csv_path}'))
            return

        created_count = 0
        skipped_count = 0

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                _, created = Ingredient.objects.get_or_create(
                    name=row['name'].strip(),
                    defaults={'unit': row['unit'].strip()},
                )
                if created:
                    created_count += 1
                else:
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Import zakończony! Dodano: {created_count}, pominięto (już istnieją): {skipped_count}.'
        ))