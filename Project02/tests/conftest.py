"""Konfiguracja testów — fixtures dla pytest."""

import pytest
from app import create_app
from app.extensions import db as _db
from app.models import User
from config import TestConfig


@pytest.fixture(scope="session")
def app():
    """Tworzy instancję aplikacji do testów."""
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Czysta baza danych dla każdego testu."""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture
def client(app, db):
    """Test client Flask."""
    return app.test_client()


@pytest.fixture
def user(db):
    """Tworzy testowego użytkownika."""
    u = User(username="testuser", email="test@test.pl")
    u.set_password("haslo123")
    db.session.add(u)
    db.session.commit()
    return u


@pytest.fixture
def logged_client(client, user):
    """Test client z zalogowanym użytkownikiem."""
    client.post("/auth/login", data={
        "username": "testuser",
        "password": "haslo123",
    })
    return client
