"""
Testy aplikacji HaluCheck.
"""

import pytest
from app import create_app


@pytest.fixture
def app():
    """Tworzy instancje aplikacji do testow."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Klient testowy Flask."""
    return app.test_client()


# ============================================================
# TESTY STRON
# ============================================================

def test_index_returns_200(client):
    """Strona glowna zwraca 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_index_contains_form(client):
    """Strona glowna zawiera formularz."""
    response = client.get("/")
    assert b"text_input" in response.data
    assert b"Sprawdz" in response.data


def test_about_returns_200(client):
    """Strona 'O projekcie' zwraca 200."""
    response = client.get("/about")
    assert response.status_code == 200


def test_about_contains_description(client):
    """Strona 'O projekcie' zawiera opis."""
    response = client.get("/about")
    assert b"HaluCheck" in response.data
    assert b"HaluEval" in response.data


def test_history_returns_200(client):
    """Strona historii zwraca 200."""
    response = client.get("/history")
    assert response.status_code == 200


def test_history_empty_by_default(client):
    """Historia jest pusta na starcie."""
    response = client.get("/history")
    assert b"Brak zapytan" in response.data


# ============================================================
# TESTY PREDYKCJI
# ============================================================

def test_predict_returns_result(client):
    """POST /predict zwraca strone z wynikiem."""
    response = client.post("/predict", data={
        "text_input": "The Eiffel Tower is located in Berlin, Germany."
    })
    assert response.status_code == 200
    assert b"Wynik analizy" in response.data


def test_predict_shows_label(client):
    """Wynik zawiera etykiete (Halucynacja lub Poprawna)."""
    response = client.post("/predict", data={
        "text_input": "Python is a programming language created by Guido van Rossum."
    })
    assert response.status_code == 200
    assert b"Halucynacja" in response.data or b"Poprawna" in response.data


def test_predict_shows_confidence(client):
    """Wynik zawiera wskaznik pewnosci."""
    response = client.post("/predict", data={
        "text_input": "Water boils at 100 degrees Celsius at sea level."
    })
    assert response.status_code == 200
    assert b"Pewnosc modelu" in response.data


# ============================================================
# TESTY WALIDACJI
# ============================================================

def test_predict_rejects_empty_text(client):
    """Pusty tekst jest odrzucany."""
    response = client.post("/predict", data={"text_input": ""}, follow_redirects=True)
    assert b"za krotki" in response.data


def test_predict_rejects_short_text(client):
    """Za krotki tekst jest odrzucany."""
    response = client.post("/predict", data={"text_input": "hello"}, follow_redirects=True)
    assert b"za krotki" in response.data


def test_predict_accepts_long_text(client):
    """Tekst powyzej minimum jest akceptowany."""
    response = client.post("/predict", data={
        "text_input": "This is a sufficiently long text for the model to process."
    })
    assert response.status_code == 200
    assert b"Wynik analizy" in response.data


# ============================================================
# TESTY HISTORII
# ============================================================

def test_history_saves_entry(client):
    """Po predykcji wpis pojawia sie w historii."""
    client.post("/predict", data={
        "text_input": "The moon is made of green cheese according to scientists."
    })
    response = client.get("/history")
    assert b"moon" in response.data


def test_history_clear(client):
    """Czyszczenie historii dziala."""
    client.post("/predict", data={
        "text_input": "Some test text for history clearing purposes."
    })
    client.post("/history/clear")
    response = client.get("/history")
    assert b"Brak zapytan" in response.data


# ============================================================
# TESTY MODEL LOADER
# ============================================================

def test_model_loader_returns_dict():
    """Funkcja predict zwraca dict z wymaganymi kluczami."""
    from app.model_loader import predict
    result = predict("The Earth orbits around the Sun once per year.")
    assert isinstance(result, dict)
    assert "label" in result
    assert "confidence" in result
    assert "label_name" in result
    assert result["label"] in (0, 1)
    assert 0.0 <= result["confidence"] <= 1.0


# ============================================================
# TESTY ROZSZERZONYCH FUNKCJI
# ============================================================

def test_predict_shows_model_panel(client):
    """Wynik zawiera panel konsylium modeli."""
    response = client.post("/predict", data={
        "text_input": "The sun orbits around the Earth once per day."
    })
    assert b"Konsylium" in response.data
    assert b"Glosowanie" in response.data


def test_predict_shows_tfidf_words(client):
    """Wynik zawiera top slowa TF-IDF."""
    response = client.post("/predict", data={
        "text_input": "The sun orbits around the Earth once per day."
    })
    assert b"Top slowa" in response.data


def test_predict_shows_feature_analysis(client):
    """Wynik zawiera analize cech tekstu."""
    response = client.post("/predict", data={
        "text_input": "The sun orbits around the Earth once per day."
    })
    assert b"Analiza cech" in response.data


def test_predict_all_models_returns_6():
    """predict_all_models zwraca wyniki dla 6 modeli."""
    from app.model_loader import predict_all_models
    results, summary = predict_all_models("Water freezes at zero degrees Celsius.")
    assert len(results) == 6
    assert "consensus" in summary


def test_analyze_features_returns_10():
    """analyze_features zwraca 10 cech."""
    from app.model_loader import analyze_features
    analysis = analyze_features("Some sample text for feature analysis.")
    assert len(analysis) == 10
    assert all("closer_to" in f for f in analysis)


def test_top_tfidf_words_returns_list():
    """get_top_tfidf_words zwraca liste slow z wagami."""
    from app.model_loader import get_top_tfidf_words
    words = get_top_tfidf_words("Machine learning is a subset of artificial intelligence.")
    assert len(words) > 0
    assert "word" in words[0]
    assert "weight" in words[0]
