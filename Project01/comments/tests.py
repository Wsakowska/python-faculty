"""Testy aplikacji comments."""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from recipes.models import Recipe
from .models import Comment


class CommentModelTest(TestCase):
    """Testy modelu Comment."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.recipe = Recipe.objects.create(
            title='Test', description='Opis',
            instructions='Instrukcje', author=self.user, prep_time=10,
        )

    def test_create_comment(self):
        """Komentarz powinien się poprawnie utworzyć."""
        comment = Comment.objects.create(
            recipe=self.recipe, author=self.user,
            content='Świetny przepis!', rating=5,
        )
        self.assertEqual(comment.rating, 5)
        self.assertIn(comment, self.recipe.comments.all())

    def test_comment_rating_str(self):
        """__str__ powinien zawierać autora, przepis i ocenę."""
        comment = Comment.objects.create(
            recipe=self.recipe, author=self.user,
            content='OK', rating=3,
        )
        self.assertIn('testuser', str(comment))
        self.assertIn('3/5', str(comment))


class AddCommentViewTest(TestCase):
    """Testy widoku dodawania komentarza."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.recipe = Recipe.objects.create(
            title='Test', description='Opis',
            instructions='Instrukcje', author=self.user, prep_time=10,
        )

    def test_add_comment_requires_login(self):
        """Dodanie komentarza wymaga logowania."""
        response = self.client.post(
            reverse('comments:add_comment', kwargs={'slug': self.recipe.slug}),
            {'content': 'Test', 'rating': 4},
        )
        self.assertEqual(response.status_code, 302)

    def test_add_comment_logged_in(self):
        """Zalogowany użytkownik może dodać komentarz."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(
            reverse('comments:add_comment', kwargs={'slug': self.recipe.slug}),
            {'content': 'Pyszne!', 'rating': 5},
        )
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(Comment.objects.first().content, 'Pyszne!')