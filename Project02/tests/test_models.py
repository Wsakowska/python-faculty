"""Testy modeli User i BirthChart."""

from datetime import date, time
from app.models import User, BirthChart


class TestUser:
    """Testy modelu User."""

    def test_create_user(self, db):
        """Tworzenie użytkownika zapisuje go w bazie."""
        u = User(username="anna", email="anna@test.pl")
        u.set_password("secret")
        db.session.add(u)
        db.session.commit()

        assert u.id is not None
        assert u.username == "anna"
        assert u.is_admin is False

    def test_password_hashing(self, db):
        """Hasło jest hashowane i poprawnie weryfikowane."""
        u = User(username="bob", email="bob@test.pl")
        u.set_password("mypassword")
        db.session.add(u)
        db.session.commit()

        assert u.check_password("mypassword") is True
        assert u.check_password("wrongpassword") is False
        assert u.password_hash != "mypassword"

    def test_user_repr(self, db):
        """__repr__ zwraca czytelną reprezentację."""
        u = User(username="repr_test", email="repr@test.pl")
        u.set_password("x")
        db.session.add(u)
        db.session.commit()

        assert "repr_test" in repr(u)


class TestBirthChart:
    """Testy modelu BirthChart."""

    def test_create_chart(self, db, user):
        """Tworzenie chartu z relacją do użytkownika."""
        chart = BirthChart(
            name="Wiktoria",
            birth_date=date(2001, 3, 28),
            birth_time=time(20, 0),
            birth_city="Starogard Gdański",
            sun_sign="Baran",
            moon_sign="Byk",
            ascendant="Waga",
            user_id=user.id,
        )
        db.session.add(chart)
        db.session.commit()

        assert chart.id is not None
        assert chart.owner == user
        assert chart.sun_sign == "Baran"

    def test_user_charts_relationship(self, db, user):
        """Użytkownik ma relację do swoich chartów."""
        for i in range(3):
            c = BirthChart(
                name=f"Chart {i}",
                birth_date=date(2000, 1, 1),
                birth_time=time(12, 0),
                birth_city="Warszawa",
                sun_sign="Koziorożec",
                user_id=user.id,
            )
            db.session.add(c)
        db.session.commit()

        assert user.charts.count() == 3

    def test_cascade_delete(self, db, user):
        """Usunięcie użytkownika usuwa jego charty."""
        chart = BirthChart(
            name="Do usunięcia",
            birth_date=date(2000, 1, 1),
            birth_time=time(12, 0),
            birth_city="Kraków",
            user_id=user.id,
        )
        db.session.add(chart)
        db.session.commit()

        db.session.delete(user)
        db.session.commit()

        assert BirthChart.query.count() == 0

    def test_chart_repr(self, db, user):
        """__repr__ zwraca czytelną reprezentację."""
        chart = BirthChart(
            name="Repr", birth_date=date(2000, 1, 1),
            birth_time=time(12, 0), birth_city="Gdańsk",
            sun_sign="Rak", user_id=user.id,
        )
        db.session.add(chart)
        db.session.commit()

        assert "Repr" in repr(chart)
