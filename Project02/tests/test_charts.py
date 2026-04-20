"""Testy widoków chartów i serwisu astrologicznego."""

from datetime import date, time
from app.charts.astro_service import (
    generate_chart, get_city_coords, SIGN_NAMES_PL,
)
from app.models import BirthChart


class TestAstroService:
    """Testy serwisu astrologicznego."""

    def test_generate_chart_valid(self, app):
        """Generowanie chartu z poprawnymi danymi."""
        with app.app_context():
            data = generate_chart("Test", 2001, 3, 28, 20, 0, "Starogard Gdański")

        assert data is not None
        assert data["sun_sign"] == "Baran"
        assert len(data["planets"]) == 10

    def test_generate_chart_unknown_city(self, app):
        """Nieznane miasto zwraca None."""
        with app.app_context():
            data = generate_chart("Test", 2000, 1, 1, 12, 0, "Atlantyda")

        assert data is None

    def test_city_coords(self):
        """Słownik miast zwraca współrzędne."""
        coords = get_city_coords("Warszawa")
        assert coords is not None
        assert abs(coords[0] - 52.23) < 0.1  # lat
        assert abs(coords[1] - 21.01) < 0.1  # lng

    def test_city_coords_case_insensitive(self):
        """Wyszukiwanie miast jest case-insensitive."""
        assert get_city_coords("GDAŃSK") is not None
        assert get_city_coords("gdańsk") is not None

    def test_sign_names_complete(self):
        """Słownik znaków zodiaku zawiera 12 znaków."""
        assert len(SIGN_NAMES_PL) == 12

    def test_planets_have_polish_names(self, app):
        """Planety mają polskie nazwy."""
        with app.app_context():
            data = generate_chart("Test", 2000, 6, 15, 12, 0, "Gdańsk")

        assert data is not None
        planet_names = [p["name_pl"] for p in data["planets"]]
        assert "Słońce" in planet_names
        assert "Księżyc" in planet_names
        assert "Merkury" in planet_names


class TestChartViews:
    """Testy widoków chartów."""

    def test_generate_page_loads(self, client):
        """Strona generowania chartu się ładuje."""
        r = client.get("/charts/generate")
        assert r.status_code == 200
        assert "Wygeneruj" in r.data.decode()

    def test_generate_chart_post(self, client):
        """POST z poprawnymi danymi przekierowuje na wynik."""
        r = client.post("/charts/generate", data={
            "name": "Test", "day": "1", "month": "1", "year": "2000",
            "hour": "12", "minute": "0", "city": "Warszawa",
        })
        assert r.status_code == 302

    def test_result_page(self, client):
        """Strona wyniku wyświetla dane chartu."""
        client.post("/charts/generate", data={
            "name": "Test", "day": "28", "month": "3", "year": "2001",
            "hour": "20", "minute": "0", "city": "Starogard Gdański",
        })
        r = client.get("/charts/result")
        assert r.status_code == 200
        assert "Baran" in r.data.decode()

    def test_result_without_session(self, client):
        """Wynik bez sesji przekierowuje na formularz."""
        r = client.get("/charts/result")
        assert r.status_code == 302

    def test_synastry_page_loads(self, client):
        """Strona synastrii się ładuje."""
        r = client.get("/charts/synastry")
        assert r.status_code == 200
        assert "Synastria" in r.data.decode()

    def test_svg_endpoint(self, client):
        """Endpoint SVG zwraca obraz po wygenerowaniu chartu."""
        client.post("/charts/generate", data={
            "name": "Test", "day": "1", "month": "6", "year": "2000",
            "hour": "12", "minute": "0", "city": "Gdańsk",
        })
        r = client.get("/charts/svg")
        assert r.status_code == 200
        assert "image/svg+xml" in r.content_type


class TestChartCRUD:
    """Testy CRUD chartów."""

    def test_save_chart(self, logged_client, db, user):
        """Zapisywanie chartu do bazy."""
        logged_client.post("/charts/generate", data={
            "name": "Save Test", "day": "1", "month": "1", "year": "2000",
            "hour": "12", "minute": "0", "city": "Warszawa",
        })
        logged_client.post("/charts/save")

        assert BirthChart.query.filter_by(user_id=user.id).count() == 1

    def test_history_page(self, logged_client, db, user):
        """Strona historii wyświetla charty użytkownika."""
        chart = BirthChart(
            name="History Test", birth_date=date(2000, 1, 1),
            birth_time=time(12, 0), birth_city="Gdańsk",
            sun_sign="Koziorożec", user_id=user.id,
        )
        db.session.add(chart)
        db.session.commit()

        r = logged_client.get("/charts/history")
        assert r.status_code == 200
        assert "History Test" in r.data.decode()

    def test_delete_chart(self, logged_client, db, user):
        """Usunięcie chartu z bazy."""
        chart = BirthChart(
            name="Delete Me", birth_date=date(2000, 1, 1),
            birth_time=time(12, 0), birth_city="Kraków",
            sun_sign="Koziorożec", user_id=user.id,
        )
        db.session.add(chart)
        db.session.commit()
        chart_id = chart.id

        logged_client.post(f"/charts/delete/{chart_id}")
        assert BirthChart.query.get(chart_id) is None


class TestAPI:
    """Testy REST API."""

    def test_api_generate_chart(self, client):
        """POST /api/chart zwraca dane chartu."""
        r = client.post("/api/chart", json={
            "name": "API Test", "year": 2001, "month": 3, "day": 28,
            "hour": 20, "minute": 0, "city": "Starogard Gdański",
        })
        assert r.status_code == 200
        data = r.get_json()
        assert data["sun_sign"] == "Baran"

    def test_api_missing_fields(self, client):
        """POST /api/chart bez wymaganych pól zwraca 400."""
        r = client.post("/api/chart", json={"name": "Test"})
        assert r.status_code == 400

    def test_api_cities(self, client):
        """GET /api/cities zwraca listę miast."""
        r = client.get("/api/cities")
        assert r.status_code == 200
        cities = r.get_json()
        assert "Warszawa" in cities

    def test_api_charts_requires_auth(self, client):
        """GET /api/charts wymaga logowania."""
        r = client.get("/api/charts")
        assert r.status_code == 302
