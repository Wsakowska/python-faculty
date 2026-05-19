# project03: Detekcja halucynacji w odpowiedziach LLM

**Autor:** Wiktoria Sakowska (274931)  
**Kurs:** Programowanie w jezyku Python | 2025/26 | Laura Grzonka  
**Data:** maj 2025

## Opis projektu

Projekt dotyczy detekcji halucynacji w odpowiedziach duzych modeli jezykowych (LLM).
Halucynacja to sytuacja, w ktorej model generuje tresci brzmiace wiarygodnie, ale niezgodne z faktami lub kontekstem.

Zadanie polega na klasyfikacji binarnej: czy dana odpowiedz jest **poprawna** (label 0) czy **halucynowana** (label 1).

## Dataset

**HaluEval** (Hallucination Evaluation Benchmark) — Li et al., 2023.

Zrodlo: [HuggingFace — pminervini/HaluEval](https://huggingface.co/datasets/pminervini/HaluEval)

Dataset sklada sie z 4 subsetow:

| Subset | Rekordow | Opis |
|---|---|---|
| QA | 10 000 | Pytania i odpowiedzi (poprawna + halucynowana) |
| Dialogue | 10 000 | Odpowiedzi w dialogu |
| Summarization | 10 000 | Podsumowania dokumentow |
| General | 4 507 | Ogolne odpowiedzi ChatGPT z labelami yes/no |

Po unifikacji i preprocessingu: **61 887 rekordow** (50.3% poprawnych, 49.7% halucynacji).

## Preprocessing

- Unifikacja 4 subsetow do jednego formatu (text + label 0/1)
- Usuwanie NaN, pustych tekstow, duplikatow
- Czyszczenie tekstu (normalizacja bialych znakow, lowercase)
- Feature engineering: 10 cech numerycznych (dlugosc tekstu, liczba slow, srednia dlugosc slowa, liczba zdan, stosunek wielkich liter, unikalne slowa, cyfry, interpunkcja)
- TF-IDF vectorization (10 000 cech, unigramy + bigramy)
- Podzial train/test: 80/20 ze stratyfikacja

## Modele

Wytrenowano 6 modeli rozniących sie algorytmem i hiperparametrami:

| Model | Accuracy | F1 | Precision | Recall | ROC AUC | Czas treningu |
|---|---|---|---|---|---|---|
| **MLP** | **0.8501** | **0.8507** | **0.8421** | **0.8595** | **0.9242** | 38.5s |
| XGBoost | 0.8468 | 0.8490 | 0.8319 | 0.8668 | 0.9270 | 109.1s |
| Random Forest | 0.8198 | 0.8292 | 0.7831 | 0.8811 | 0.9110 | 1.5s |
| Linear SVM | 0.8148 | 0.8110 | 0.8221 | 0.8003 | 0.8899 | 2.5s |
| Logistic Regression | 0.8019 | 0.7969 | 0.8120 | 0.7824 | 0.8773 | 5.8s |
| Naive Bayes | 0.7231 | 0.7183 | 0.7261 | 0.7106 | 0.7884 | 0.0s |

### Najlepszy model: MLP (Multi-Layer Perceptron)

Siec neuronowa z 2 warstwami ukrytymi (256, 128 neuronow), aktywacja ReLU, optymalizator Adam.
Wybrana na podstawie najwyzszego F1 score (0.8507), ktory rownowazy precision i recall.

MLP osiaga najlepsza rownowage miedzy precision a recall, co jest kluczowe w detekcji halucynacji — zalezy nam zarowno na wykrywaniu halucynacji (recall), jak i na unikaniu falszywych alarmow (precision).

## Struktura projektu

```
project03/
├── data/
│   ├── raw/                  # surowe dane HaluEval (nie w repo)
│   └── processed/            # dane po preprocessingu (nie w repo)
├── models/                   # zapisane modele .pkl (nie w repo)
├── notebooks/
│   └── 01_eda.py             # Exploratory Data Analysis
├── results/
│   ├── figures/              # wykresy
│   └── metrics/              # metryki modeli (CSV)
├── src/
│   ├── __init__.py
│   ├── preprocessing.py      # unifikacja i czyszczenie danych
│   ├── features.py           # TF-IDF, feature engineering, train/test split
│   ├── evaluation.py         # metryki, confusion matrix, ROC, wykresy
│   └── models.py             # definicje i trening 6 modeli ML
├── setup_project.py          # pobieranie danych i tworzenie struktury
├── requirements.txt
├── .gitignore
└── README.md
```

## Uruchomienie

```bash
# 1. Srodowisko wirtualne
python3 -m venv venv
source venv/bin/activate

# 2. Instalacja zaleznosci
pip install -r requirements.txt

# 3. Pobranie danych i setup
python setup_project.py

# 4. Preprocessing
python src/preprocessing.py

# 5. Feature extraction
python src/features.py

# 6. EDA (opcjonalnie — generuje wykresy)
python notebooks/01_eda.py

# 7. Trening i ewaluacja modeli
python src/models.py
```

## Wymagania

- Python 3.10+
- Biblioteki: patrz `requirements.txt`

## Wizualizacje

Wykresy generowane przez projekt:
- Rozklad labeli (ogolny i per subset)
- Rozklad dlugosci tekstu per label
- Heatmapa korelacji cech
- Violin plots kluczowych cech
- Top 20 slow (poprawne vs halucynacje)
- Macierz bledow dla kazdego modelu
- Krzywe ROC (porownanie modeli)
- Porownanie metryk modeli
- Krzywa uczenia najlepszego modelu

## Zrodla

- Li, J. et al. (2023). *HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models.* EMNLP 2023. https://github.com/RUCAIBox/HaluEval
- Dataset: https://huggingface.co/datasets/pminervini/HaluEval (licencja Apache 2.0)
- scikit-learn: Pedregosa, F. et al. (2011). Scikit-learn: Machine Learning in Python. JMLR 12. https://scikit-learn.org/ (wersja >= 1.3.0)
- pandas: https://pandas.pydata.org/ (wersja >= 2.0.0)
- matplotlib: https://matplotlib.org/ (wersja >= 3.7.0)
- seaborn: https://seaborn.pydata.org/ (wersja >= 0.12.0)

### AI

W trakcie realizacji projektu korzystano z modelu Claude Opus 4 (Anthropic, maj 2025) jako wsparcia przy:
- generowaniu szkieletu kodu (struktura plikow, boilerplate)
- debugowaniu bledow
- doborze hiperparametrow modeli

Wiekszosc pracy koncepcyjnej (wybor tematu, dobor modeli, interpretacja wynikow, dokumentacja) wykonana samodzielnie.