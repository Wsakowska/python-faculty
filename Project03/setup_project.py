import os
import json
import pandas as pd
from datasets import load_dataset

# ============================================================
# 1. KONFIGURACJA ŚCIEŻEK
# ============================================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "data", "processed")

# Utwórz katalogi
for d in [DATA_DIR, PROCESSED_DIR,
          os.path.join(PROJECT_ROOT, "notebooks"),
          os.path.join(PROJECT_ROOT, "src"),
          os.path.join(PROJECT_ROOT, "models"),
          os.path.join(PROJECT_ROOT, "results", "figures"),
          os.path.join(PROJECT_ROOT, "results", "metrics")]:
    os.makedirs(d, exist_ok=True)
    print(f"Katalog: {d}")

# ============================================================
# 2. POBIERANIE DATASETU HaluEval
# ============================================================
SUBSETS = ["qa", "dialogue", "summarization", "general"]

print("\n" + "=" * 60)
print("Pobieranie HaluEval z HuggingFace...")
print("=" * 60)

for subset_name in SUBSETS:
    print(f"\n--- Subset: {subset_name} ---")
    
    ds = load_dataset("pminervini/HaluEval", subset_name, split="data")
    
    # Info o datasecie
    print(f"  Wierszy: {len(ds)}")
    print(f"  Kolumny: {ds.column_names}")
    
    # Zapisz jako JSON (oryginalny format)
    json_path = os.path.join(DATA_DIR, f"{subset_name}_data.json")
    ds.to_json(json_path)
    print(f"Zapisano: {json_path}")
    
    # Zapisz też jako CSV (wygodniejszy do pracy z pandas)
    csv_path = os.path.join(DATA_DIR, f"{subset_name}_data.csv")
    df = ds.to_pandas()
    df.to_csv(csv_path, index=False)
    print(f"Zapisano: {csv_path}")
    
    # Pokaż przykład
    print(f"\n Przykładowy rekord:")
    example = ds[0]
    for key, val in example.items():
        val_str = str(val)[:120]
        print(f"     {key}: {val_str}{'...' if len(str(val)) > 120 else ''}")

# ============================================================
# 3. PODSUMOWANIE STATYSTYCZNE
# ============================================================
print("\n" + "=" * 60)
print("PODSUMOWANIE DATASETU")
print("=" * 60)

total = 0
for subset_name in SUBSETS:
    csv_path = os.path.join(DATA_DIR, f"{subset_name}_data.csv")
    df = pd.read_csv(csv_path)
    total += len(df)
    print(f"  {subset_name:20s} → {len(df):>6,} wierszy | kolumny: {list(df.columns)}")

print(f"\n  {'RAZEM':20s} → {total:>6,} wierszy")

# ============================================================
# 4. INFO O STRUKTURZE PROJEKTU
# ============================================================
print("\n" + "=" * 60)
print("STRUKTURA PROJEKTU")
print("=" * 60)
print("""
project03/
├── data/
│   ├── raw/              ← surowe dane (właśnie pobrane!)
│   └── processed/        ← dane po preprocessingu
├── notebooks/            ← Jupyter notebooks (EDA, eksperymenty)
├── src/                  ← kod źródłowy (moduły Pythonowe)
│   ├── __init__.py
│   ├── preprocessing.py  ← czyszczenie i przygotowanie danych
│   ├── features.py       ← feature engineering (TF-IDF, embeddingi)
│   ├── models.py         ← definicje modeli ML
│   ├── evaluation.py     ← metryki, confusion matrix, wykresy
│   └── utils.py          ← funkcje pomocnicze
├── models/               ← zapisane wytrenowane modele (.pkl)
├── results/
│   ├── figures/          ← wykresy, wizualizacje
│   └── metrics/          ← wyniki metryk (CSV/JSON)
├── setup_project.py      ← TEN SKRYPT
├── main.py               ← główny pipeline
├── requirements.txt
└── README.md
""")

print("Setup zakończony! Teraz możesz zacząć od notebooks/01_eda.ipynb")
print("lub uruchomić main.py po przygotowaniu modeli.")
