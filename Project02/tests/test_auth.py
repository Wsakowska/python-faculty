"""Testy widoków autoryzacji (rejestracja, logowanie, profil)."""

from app.models import User


class TestRegister:
    """Testy rejestracji."""

    def test_register_page_loads(self, client):
        """Strona rejestracji się ładuje."""
        r = client.get("/auth/register")
        assert r.status_code == 200
        assert "Rejestracja" in r.data.decode()

    def test_register_creates_user(self, client, db):
        """Rejestracja tworzy nowego użytkownika."""
        r = client.post("/auth/register", data={
            "username": "newuser",
            "email": "new@test.pl",
            "password": "haslo123",
            "password2": "haslo123",
        }, follow_redirects=True)

        assert r.status_code == 200
        assert User.query.filter_by(username="newuser").first() is not None

    def test_register_duplicate_username(self, client, db, user):
        """Rejestracja z zajętą nazwą użytkownika nie przechodzi."""
        r = client.post("/auth/register", data={
            "username": "testuser",  # taki sam jak fixture user
            "email": "other@test.pl",
            "password": "haslo123",
            "password2": "haslo123",
        })

        assert r.status_code == 200
        assert "zajęta" in r.data.decode()


class TestLogin:
    """Testy logowania."""

    def test_login_page_loads(self, client):
        """Strona logowania się ładuje."""
        r = client.get("/auth/login")
        assert r.status_code == 200
        assert "Logowanie" in r.data.decode()

    def test_login_valid(self, client, user):
        """Logowanie poprawnymi danymi działa."""
        r = client.post("/auth/login", data={
            "username": "testuser",
            "password": "haslo123",
        }, follow_redirects=True)

        assert r.status_code == 200
        assert "Witaj" in r.data.decode()

    def test_login_invalid(self, client, user):
        """Logowanie złym hasłem nie przechodzi."""
        r = client.post("/auth/login", data={
            "username": "testuser",
            "password": "zlehaslo",
        }, follow_redirects=True)

        assert r.status_code == 200
        assert "Nieprawidłowa" in r.data.decode()


class TestProfile:
    """Testy profilu."""

    def test_profile_requires_login(self, client):
        """Profil wymaga zalogowania."""
        r = client.get("/auth/profile")
        assert r.status_code == 302

    def test_profile_shows_username(self, logged_client, user):
        """Profil wyświetla nazwę użytkownika."""
        r = logged_client.get("/auth/profile")
        assert r.status_code == 200
        assert "testuser" in r.data.decode()
