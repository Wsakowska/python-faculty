"""Testy aplikacji accounts."""

from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import UserProfile, DietaryPreference


class UserProfileModelTest(TestCase):
    """Testy modelu UserProfile."""

    def test_create_profile(self):
        """Profil powinien się powiązać z użytkownikiem."""
        user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        profile = UserProfile.objects.create(user=user)
        self.assertEqual(str(profile), 'Profil: testuser')
        self.assertEqual(user.profile, profile)

    def test_dietary_preferences(self):
        """Profil może mieć wiele preferencji dietetycznych."""
        user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        profile = UserProfile.objects.create(user=user)
        pref1 = DietaryPreference.objects.create(name='Wegetariańskie')
        pref2 = DietaryPreference.objects.create(name='Bezglutenowe')
        profile.dietary_preferences.add(pref1, pref2)
        self.assertEqual(profile.dietary_preferences.count(), 2)


class RegisterViewTest(TestCase):
    """Testy widoku rejestracji."""

    def test_register_page_status(self):
        """Strona rejestracji powinna zwracać status 200."""
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)

    def test_register_new_user(self):
        """Rejestracja powinna utworzyć nowego użytkownika."""
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'SuperTajne123!',
            'password2': 'SuperTajne123!',
        })
        self.assertEqual(response.status_code, 302)  # redirect po rejestracji
        self.assertTrue(User.objects.filter(username='newuser').exists())


class LoginViewTest(TestCase):
    """Testy widoku logowania."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_login_page_status(self):
        """Strona logowania powinna zwracać status 200."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_valid_user(self):
        """Logowanie z poprawnymi danymi powinno przekierować."""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)