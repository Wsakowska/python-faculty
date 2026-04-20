#  AstroApp

Aplikacja webowa do generowania map urodzeniowych (natal charts) i synastrii.
Projekt z Programowania w języku Python — Flask (Uniwersytet Gdański, 2025).

**Autorka:** Wiktoria Sakowska (274931)  
**Prowadząca:** mgr Laura Grzonka

## Funkcjonalności

- **Mapa urodzeniowa** — obliczenia astrologiczne + wizualizacja SVG (kerykeion)
- **Synastria** — porównanie dwóch map urodzeniowych
- **Interpretacja AI** — spersonalizowana analiza chartu (Google Gemini)
- **Konta użytkowników** — rejestracja, logowanie, profil, historia chartów
- **CRUD** — zapisywanie, edycja, usuwanie chartów
- **Wyszukiwarka** — szukaj po imieniu, znaku zodiaku, mieście
- **REST API** — endpointy JSON do generowania i pobierania chartów

## Instalacja

```bash
# Klonowanie i wejście do projektu
git clone <URL>
cd Project02

# Środowisko wirtualne
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Zależności
pip install -r requirements.txt

# Klucz API Gemini (opcjonalne — bez tego AI nie działa, reszta tak)
export GEMINI_API_KEY="twoj-klucz-z-aistudio.google.com"

# Baza danych
flask db init
flask db migrate -m "Initial"
flask db upgrade

# Uruchomienie
python run.py
```

Aplikacja dostępna pod: `http://127.0.0.1:5000`

## Struktura projektu

```
Project02/
├── app/
│   ├── __init__.py         # Application factory
│   ├── extensions.py       # db, login_manager, csrf
│   ├── models.py           # User, BirthChart
│   ├── main/               # Strona główna, about, wyszukiwarka
│   ├── auth/               # Rejestracja, logowanie, profil
│   ├── charts/             # Generowanie chartów, synastria, CRUD, AI
│   ├── api/                # REST API (JSON)
│   ├── templates/          # base.html, 404, 500
│   └── static/css/         # Własne style
├── tests/                  # 34 testy (pytest)
├── config.py               # Config + TestConfig
├── run.py                  # Entry point
├── requirements.txt
├── SOURCES.md              # Bibliografia
└── docs/                   # Dokumentacja LaTeX
```

## Dostępne adresy

| Adres | Opis |
|-------|------|
| `/` | Strona główna |
| `/charts/generate` | Generowanie chartu |
| `/charts/synastry` | Synastria |
| `/charts/history` | Historia chartów (wymaga logowania) |
| `/search` | Wyszukiwarka |
| `/auth/register` | Rejestracja |
| `/auth/login` | Logowanie |
| `/auth/profile` | Profil |
| `/about` | O aplikacji |
| `/api/chart` | REST API — generowanie chartu (POST) |
| `/api/charts` | REST API — lista chartów (GET) |
| `/api/cities` | REST API — lista miast (GET) |

## Testy

```bash
python -m pytest tests/ -v
```

34 testy: modele, autoryzacja, generowanie chartów, CRUD, REST API.

## Technologie

| Technologia | Zastosowanie |
|-------------|-------------|
| Flask 3.1 | Framework webowy |
| SQLAlchemy + Flask-Migrate | Baza danych (SQLite) |
| Flask-Login + Flask-WTF | Autoryzacja, formularze, CSRF |
| kerykeion 5.x | Obliczenia astrologiczne |
| google-genai | Interpretacja AI (Gemini) |
| Bootstrap 5.3 | Stylizacja (dark mode) |
| pytest | Testy |

## Spełnienie wymagań

**Niezbędne:** 12+ podstron, CRUD, 5+ widoków, 4 blueprinty, formularze, obsługa 404/500, testy.

**Opcje dodatkowe (6/3):** stylizacja Bootstrap, Jinja2, REST API, konta użytkowników, chat AI (Gemini), przeszukiwanie strony.

Pełna dokumentacja: `docs/dokumentacja.pdf`  
Bibliografia: `SOURCES.md`