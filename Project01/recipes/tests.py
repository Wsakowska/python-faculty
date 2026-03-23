"""Testy aplikacji recipes."""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Category, Ingredient, Recipe, RecipeIngredient
from .forms import RecipeForm, IngredientSearchForm


class CategoryModelTest(TestCase):
    """Testy modelu Category."""

    def test_create_category(self):
        """Kategoria powinna się utworzyć z automatycznym slugiem."""
        category = Category.objects.create(name='Śniadanie')
        self.assertEqual(str(category), 'Śniadanie')
        self.assertEqual(category.slug, 'sniadanie')

    def test_category_unique_name(self):
        """Nazwa kategorii musi być unikalna."""
        Category.objects.create(name='Obiad')
        with self.assertRaises(Exception):
            Category.objects.create(name='Obiad')


class IngredientModelTest(TestCase):
    """Testy modelu Ingredient."""

    def test_create_ingredient(self):
        """Składnik powinien się poprawnie utworzyć."""
        ingredient = Ingredient.objects.create(name='Jajko', unit='szt')
        self.assertEqual(str(ingredient), 'Jajko')
        self.assertEqual(ingredient.unit, 'szt')

    def test_default_unit(self):
        """Domyślna jednostka to 'szt'."""
        ingredient = Ingredient.objects.create(name='Masło')
        self.assertEqual(ingredient.unit, 'szt')


class RecipeModelTest(TestCase):
    """Testy modelu Recipe."""

    def setUp(self):
        """Przygotowanie danych testowych."""
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.category = Category.objects.create(name='Obiad')
        self.recipe = Recipe.objects.create(
            title='Makaron z sosem',
            description='Pyszny makaron.',
            instructions='Ugotuj makaron. Dodaj sos.',
            author=self.user,
            category=self.category,
            prep_time=20,
            difficulty='easy',
        )

    def test_create_recipe(self):
        """Przepis powinien się poprawnie utworzyć."""
        self.assertEqual(str(self.recipe), 'Makaron z sosem')
        self.assertEqual(self.recipe.slug, 'makaron-z-sosem')

    def test_recipe_author_relation(self):
        """Przepis powinien być powiązany z autorem."""
        self.assertEqual(self.recipe.author, self.user)
        self.assertIn(self.recipe, self.user.recipes.all())

    def test_recipe_category_relation(self):
        """Przepis powinien być powiązany z kategorią."""
        self.assertEqual(self.recipe.category, self.category)
        self.assertIn(self.recipe, self.category.recipes.all())

    def test_recipe_default_published(self):
        """Przepis domyślnie jest opublikowany."""
        self.assertTrue(self.recipe.is_published)


class RecipeIngredientModelTest(TestCase):
    """Testy modelu RecipeIngredient (tabela pośrednia)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.recipe = Recipe.objects.create(
            title='Test', description='Test',
            instructions='Test', author=self.user, prep_time=10,
        )
        self.ingredient = Ingredient.objects.create(name='Mąka', unit='g')

    def test_add_ingredient_to_recipe(self):
        """Składnik powinien zostać powiązany z przepisem przez tabelę pośrednią."""
        ri = RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ingredient, amount=200,
        )
        self.assertEqual(str(ri), '200 g Mąka')
        self.assertIn(self.ingredient, self.recipe.ingredients.all())


class RecipeFormTest(TestCase):
    """Testy formularza RecipeForm."""

    def setUp(self):
        self.category = Category.objects.create(name='Deser')

    def test_valid_form(self):
        """Formularz z poprawnymi danymi powinien być valid."""
        data = {
            'title': 'Ciasto',
            'description': 'Pyszne ciasto.',
            'instructions': 'Piecz 30 min.',
            'category': self.category.id,
            'prep_time': 30,
            'difficulty': 'medium',
        }
        form = RecipeForm(data=data)
        self.assertTrue(form.is_valid())

    def test_empty_title(self):
        """Formularz bez tytułu powinien być invalid."""
        data = {
            'title': '',
            'description': 'Opis.',
            'instructions': 'Instrukcje.',
            'prep_time': 10,
            'difficulty': 'easy',
        }
        form = RecipeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class IngredientSearchFormTest(TestCase):
    """Testy formularza wyszukiwania."""

    def setUp(self):
        self.ing1 = Ingredient.objects.create(name='Jajko', unit='szt')
        self.ing2 = Ingredient.objects.create(name='Mleko', unit='ml')

    def test_valid_search(self):
        """Formularz z wybranymi składnikami powinien być valid."""
        data = {'ingredients': [self.ing1.id, self.ing2.id]}
        form = IngredientSearchForm(data=data)
        self.assertTrue(form.is_valid())

    def test_empty_search(self):
        """Formularz bez składników powinien być invalid."""
        form = IngredientSearchForm(data={'ingredients': []})
        self.assertFalse(form.is_valid())


class HomeViewTest(TestCase):
    """Testy widoku strony głównej."""

    def test_home_page_status(self):
        """Strona główna powinna zwracać status 200."""
        response = self.client.get(reverse('recipes:home'))
        self.assertEqual(response.status_code, 200)

    def test_home_uses_correct_template(self):
        """Strona główna powinna używać szablonu home.html."""
        response = self.client.get(reverse('recipes:home'))
        self.assertTemplateUsed(response, 'recipes/home.html')


class RecipeListViewTest(TestCase):
    """Testy widoku listy przepisów."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.recipe = Recipe.objects.create(
            title='Testowy przepis', description='Opis',
            instructions='Instrukcje', author=self.user, prep_time=15,
        )

    def test_recipe_list_status(self):
        """Lista przepisów powinna zwracać status 200."""
        response = self.client.get(reverse('recipes:recipe_list'))
        self.assertEqual(response.status_code, 200)

    def test_recipe_list_contains_recipe(self):
        """Lista powinna zawierać utworzony przepis."""
        response = self.client.get(reverse('recipes:recipe_list'))
        self.assertContains(response, 'Testowy przepis')


class RecipeDetailViewTest(TestCase):
    """Testy widoku szczegółów przepisu."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.recipe = Recipe.objects.create(
            title='Detale test', description='Opis',
            instructions='Instrukcje', author=self.user, prep_time=10,
        )

    def test_recipe_detail_status(self):
        """Strona przepisu powinna zwracać status 200."""
        response = self.client.get(
            reverse('recipes:recipe_detail', kwargs={'slug': self.recipe.slug})
        )
        self.assertEqual(response.status_code, 200)

    def test_recipe_detail_404(self):
        """Nieistniejący przepis powinien zwrócić 404."""
        response = self.client.get(
            reverse('recipes:recipe_detail', kwargs={'slug': 'nie-istnieje'})
        )
        self.assertEqual(response.status_code, 404)


class RecipeCreateViewTest(TestCase):
    """Testy widoku tworzenia przepisu."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_create_requires_login(self):
        """Dodawanie przepisu wymaga logowania."""
        response = self.client.get(reverse('recipes:recipe_create'))
        self.assertEqual(response.status_code, 302)  # redirect do logowania

    def test_create_page_for_logged_user(self):
        """Zalogowany użytkownik widzi formularz dodawania."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('recipes:recipe_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dodaj przepis')


class RecipeSearchViewTest(TestCase):
    """Testy widoku wyszukiwarki."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.ing = Ingredient.objects.create(name='Jajko', unit='szt')
        self.recipe = Recipe.objects.create(
            title='Jajecznica', description='Prosta jajecznica',
            instructions='Smaż jajka', author=self.user, prep_time=5,
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=self.ing, amount=3,
        )

    def test_search_page_status(self):
        """Wyszukiwarka powinna zwracać status 200."""
        response = self.client.get(reverse('recipes:recipe_search'))
        self.assertEqual(response.status_code, 200)

    def test_search_finds_recipe(self):
        """Wyszukiwarka powinna znaleźć przepis z danym składnikiem."""
        response = self.client.get(
            reverse('recipes:recipe_search'),
            {'ingredients': [self.ing.id]},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Jajecznica')

    def test_search_no_results(self):
        """Wyszukiwarka z nieistniejącym składnikiem — brak wyników."""
        other_ing = Ingredient.objects.create(name='Kawior', unit='g')
        response = self.client.get(
            reverse('recipes:recipe_search'),
            {'ingredients': [other_ing.id]},
        )
        self.assertContains(response, 'Nie znaleziono przepisów')