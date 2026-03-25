# 🍳 Co mam w lodówce?

Aplikacja webowa w Django pozwalająca wyszukiwać przepisy kulinarne na podstawie składników, które użytkownik aktualnie posiada.

**Autorka:** Wiktoria Sakowska (274931)  
**Przedmiot:** Programowanie w języku Python (2025/26)  
**Prowadząca:** mgr Laura Grzonka  
**Uniwersytet Gdański, WMFiI**

## Uruchomienie

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
# Otwórz http://127.0.0.1:8000
```

Dla asystenta AI — stwórz plik `.env` z kluczem: `GEMINI_API_KEY=twoj_klucz`

## Główne funkcjonalności

- Wyszukiwarka przepisów po zaznaczonych składnikach (ranking dopasowania)
- Pełny CRUD przepisów z formsetem składników
- Konta użytkowników (rejestracja, logowanie, profil z preferencjami)
- Komentarze z ocenami 1–5 gwiazdek
- Rekomendacje na podstawie preferencji dietetycznych
- Asystent kucharski AI (Google Gemini)
- REST API z dokumentacją Swagger UI (`/api/docs/`)

## Dokumentacja

Pełna dokumentacja projektu: **`docs/dokumentacja.pdf`**  
Źródła i podział pracy: **`SOURCES.md`**