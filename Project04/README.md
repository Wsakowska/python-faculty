# HaluCheck

Aplikacja webowa do wykrywania halucynacji w tekstach generowanych przez modele AI.

Projekt IV z przedmiotu Programowanie w jezyku Python (2025/26, Uniwersytet Gdanski).

## Opis

HaluCheck laczy dwa wczesniejsze projekty:
- **Project03** — klasyfikator halucynacji (MLP) wytrenowany na zbiorze HaluEval
- **Aplikacja webowa Flask** — interfejs umozliwiajacy uzytkownikom sprawdzenie tekstu pod katem halucynacji

Uzytkownik wpisuje tekst wygenerowany przez AI, a aplikacja zwraca predykcje (halucynacja / brak halucynacji) wraz ze wskaznikiem pewnosci modelu.

## Funkcjonalnosci

- Analiza tekstu pod katem halucynacji z uzyciem modelu MLP
- Wyswietlanie wyniku z paskiem pewnosci modelu
- Historia zapytan w sesji przegladarki (do 20 wpisow)
- Strona informacyjna o projekcie i ograniczeniach modelu
- Walidacja danych wejsciowych (minimalna dlugosc tekstu)
- Responsywny interfejs (Bootstrap 5)

## Technologie

- Python 3.13
- Flask 3.1.1
- scikit-learn 1.6.1 (MLPClassifier)
- scipy 1.15.2 (macierze sparse)
- Bootstrap 5.3.3
- pytest 8.3.5

## Struktura projektu

```
project04-halucheck/
├── app/
│   ├── __init__.py          # app factory (create_app)
│   ├── routes.py            # endpointy: /, /predict, /history, /about
│   ├── model_loader.py      # ladowanie MLP, preprocessing, predykcja
│   ├── templates/
│   │   ├── base.html        # szablon bazowy z navbar i footer
│   │   ├── index.html       # formularz do wpisania tekstu
│   │   ├── result.html      # wynik predykcji z paskiem pewnosci
│   │   ├── history.html     # tabela historii zapytan
│   │   └── about.html       # opis projektu i modelu
│   └── static/
│       └── css/
│           └── style.css    # dodatkowe style
├── model/
│   ├── mlp.pkl              # wytrenowany model MLP z Project03
│   └── tfidf_vectorizer.pkl # dopasowany TfidfVectorizer z Project03
├── tests/
│   ├── __init__.py
│   └── test_app.py          # 15 testow pytest
├── run.py                   # punkt wejscia
├── requirements.txt
├── LICENSE
└── README.md
```

## Uruchomienie

```bash
cd project04
python3.13 -m venv venv
source venv/bin/activate          # Linux/Mac
# venv\Scripts\activate           # Windows
pip install -r requirements.txt
python run.py
```

Aplikacja dostepna pod adresem: http://127.0.0.1:5000

## Testy

```bash
python -m pytest tests/ -v
```

## Jak dziala model

1. Uzytkownik wpisuje tekst w formularzu.
2. Tekst przechodzi preprocessing (czyszczenie, lowercase).
3. Z oryginalnego tekstu wyodrebniane sa cechy numeryczne (10 cech: dlugosc, liczba slow, unikalne slowa, interpunkcja itp.).
4. Tekst jest transformowany przez TF-IDF vectorizer (10 000 cech, unigramy + bigramy).
5. Cechy TF-IDF i numeryczne sa laczone (10 010 cech).
6. Model MLP (warstwy: 256, 128 neuronow) zwraca predykcje i prawdopodobienstwo.

Model wytrenowany na zbiorze **HaluEval** (subsety: QA, dialogue, summarization, general).

## Ograniczenia

- Model dziala najlepiej na tekstach w jezyku angielskim.
- Trenowany na danych z HaluEval — moze nie generalizowac na inne domeny.
- Predykcja to oszacowanie prawdopodobienstwa, nie pewnosc.

## Autorka

Wiktoria — studentka Informatyki Ogolnoakademickiej, Uniwersytet Gdanski (274931)

### Biblioteki i frameworki

- Flask 3.1.1 — https://flask.palletsprojects.com/
- scikit-learn 1.6.1 — https://scikit-learn.org/
- Bootstrap 5.3.3 — https://getbootstrap.com/
- Bootstrap Icons 1.11.3 — https://icons.getbootstrap.com/
- pytest 8.3.5 — https://docs.pytest.org/

### Dane

- HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models — https://github.com/RUCAIBox/HaluEval

