"""
Preprocessing danych HaluEval
==============================
project03: Detekcja halucynacji w odpowiedziach LLM

Moduł unifikuje 4 subsety HaluEval do jednego datasetu binarnej klasyfikacji:
    - text: tekst odpowiedzi/podsumowania
    - label: 0 = poprawna odpowiedź, 1 = halucynacja
    - source: subset źródłowy (qa, dialogue, summarization, general)
    - context: kontekst (pytanie, dialog, dokument źródłowy)
"""

import os
import pandas as pd
import numpy as np
import re
import string
from collections import Counter


# ============================================================
# 1. ŁADOWANIE I UNIFIKACJA SUBSETÓW
# ============================================================

def load_qa_subset(path: str) -> pd.DataFrame:
    """
    Subset QA: każdy wiersz ma right_answer i hallucinated_answer.
    Tworzymy 2 rekordy na wiersz (poprawna + halucynacja).
    """
    df = pd.read_csv(path)
    
    correct = pd.DataFrame({
        "text": df["right_answer"],
        "label": 0,
        "source": "qa",
        "context": df["question"],
        "knowledge": df["knowledge"],
    })
    
    hallucinated = pd.DataFrame({
        "text": df["hallucinated_answer"],
        "label": 1,
        "source": "qa",
        "context": df["question"],
        "knowledge": df["knowledge"],
    })
    
    return pd.concat([correct, hallucinated], ignore_index=True)


def load_dialogue_subset(path: str) -> pd.DataFrame:
    """
    Subset Dialogue: right_response vs hallucinated_response.
    """
    df = pd.read_csv(path)
    
    correct = pd.DataFrame({
        "text": df["right_response"],
        "label": 0,
        "source": "dialogue",
        "context": df["dialogue_history"],
        "knowledge": df["knowledge"],
    })
    
    hallucinated = pd.DataFrame({
        "text": df["hallucinated_response"],
        "label": 1,
        "source": "dialogue",
        "context": df["dialogue_history"],
        "knowledge": df["knowledge"],
    })
    
    return pd.concat([correct, hallucinated], ignore_index=True)


def load_summarization_subset(path: str) -> pd.DataFrame:
    """
    Subset Summarization: right_summary vs hallucinated_summary.
    """
    df = pd.read_csv(path)
    
    correct = pd.DataFrame({
        "text": df["right_summary"],
        "label": 0,
        "source": "summarization",
        "context": df["document"],
        "knowledge": "",
    })
    
    hallucinated = pd.DataFrame({
        "text": df["hallucinated_summary"],
        "label": 1,
        "source": "summarization",
        "context": df["document"],
        "knowledge": "",
    })
    
    return pd.concat([correct, hallucinated], ignore_index=True)


def load_general_subset(path: str) -> pd.DataFrame:
    """
    Subset General: ma kolumnę 'hallucination' (yes/no) — naturalny label.
    """
    df = pd.read_csv(path)
    
    result = pd.DataFrame({
        "text": df["chatgpt_response"],
        "label": df["hallucination"].map({"yes": 1, "no": 0}),
        "source": "general",
        "context": df["user_query"],
        "knowledge": "",
    })
    
    return result


def load_and_unify(data_dir: str) -> pd.DataFrame:
    """
    Ładuje wszystkie 4 subsety i łączy w jeden DataFrame.
    
    Returns:
        pd.DataFrame z kolumnami: text, label, source, context, knowledge
    """
    print("Ladowanie subsetow...")
    
    loaders = {
        "qa": load_qa_subset,
        "dialogue": load_dialogue_subset,
        "summarization": load_summarization_subset,
        "general": load_general_subset,
    }
    
    dfs = []
    for name, loader_fn in loaders.items():
        path = os.path.join(data_dir, f"{name}_data.csv")
        df = loader_fn(path)
        dfs.append(df)
        print(f"  [OK] {name}: {len(df)} rekordow (label=0: {(df['label']==0).sum()}, label=1: {(df['label']==1).sum()})")
    
    unified = pd.concat(dfs, ignore_index=True)
    print(f"\nZunifikowany dataset: {len(unified)} rekordow")
    print(f"   Label 0 (poprawne):     {(unified['label']==0).sum()}")
    print(f"   Label 1 (halucynacje):  {(unified['label']==1).sum()}")
    
    return unified


# ============================================================
# 2. CZYSZCZENIE TEKSTU
# ============================================================

def clean_text(text: str) -> str:
    """
    Podstawowe czyszczenie tekstu:
    - usunięcie nadmiarowych białych znaków
    - usunięcie znaków specjalnych (z zachowaniem interpunkcji)
    - lowercase
    """
    if not isinstance(text, str):
        return ""
    
    # Normalizacja białych znaków
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Lowercase
    text = text.lower()
    
    return text


def add_text_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Dodaje cechy inżynierowane z tekstu (feature engineering):
    - text_len: długość tekstu (znaki)
    - word_count: liczba słów
    - avg_word_len: średnia długość słowa
    - sentence_count: liczba zdań (przybliżona)
    - exclamation_count: liczba wykrzykników
    - question_mark_count: liczba znaków zapytania
    - uppercase_ratio: stosunek wielkich liter do wszystkich
    - unique_word_ratio: stosunek unikalnych słów do wszystkich
    - digit_count: liczba cyfr
    - punctuation_ratio: stosunek znaków interpunkcyjnych
    """
    df = df.copy()
    
    # Długość tekstu
    df["text_len"] = df["text"].str.len()
    
    # Liczba słów
    df["word_count"] = df["text"].str.split().str.len()
    
    # Średnia długość słowa
    df["avg_word_len"] = df["text"].apply(
        lambda x: np.mean([len(w) for w in str(x).split()]) if isinstance(x, str) and len(x) > 0 else 0
    )
    
    # Liczba zdań (przybliżona — po '.', '!', '?')
    df["sentence_count"] = df["text"].str.count(r'[.!?]+')
    
    # Znaki specjalne
    df["exclamation_count"] = df["text"].str.count("!")
    df["question_mark_count"] = df["text"].str.count(r'\?')
    
    # Uppercase ratio (na oryginalnym tekście, przed lowercasem)
    df["uppercase_ratio"] = df["text"].apply(
        lambda x: sum(1 for c in str(x) if c.isupper()) / max(len(str(x)), 1)
    )
    
    # Unique word ratio
    df["unique_word_ratio"] = df["text"].apply(
        lambda x: len(set(str(x).lower().split())) / max(len(str(x).split()), 1)
    )
    
    # Cyfry
    df["digit_count"] = df["text"].str.count(r'\d')
    
    # Punctuation ratio
    df["punctuation_ratio"] = df["text"].apply(
        lambda x: sum(1 for c in str(x) if c in string.punctuation) / max(len(str(x)), 1)
    )
    
    return df


# ============================================================
# 3. GŁÓWNA FUNKCJA PREPROCESSINGU
# ============================================================

def preprocess_pipeline(raw_dir: str, processed_dir: str) -> pd.DataFrame:
    """
    Pełny pipeline preprocessingu:
    1. Ładowanie i unifikacja subsetów
    2. Usunięcie NaN i duplikatów
    3. Czyszczenie tekstu
    4. Feature engineering
    5. Zapis do pliku
    
    Returns:
        pd.DataFrame gotowy do modelowania
    """
    # 1. Ładowanie
    df = load_and_unify(raw_dir)
    
    # 2. Czyszczenie danych
    print("\nCzyszczenie danych...")
    initial_len = len(df)
    
    # Usunięcie NaN w kluczowych kolumnach
    df = df.dropna(subset=["text", "label"])
    
    # Usunięcie pustych tekstów
    df = df[df["text"].str.strip().str.len() > 0]
    
    # Usunięcie duplikatów (po tekście)
    df = df.drop_duplicates(subset=["text"], keep="first")
    
    print(f"  Usunięto {initial_len - len(df)} rekordów (NaN/puste/duplikaty)")
    print(f"  Pozostało: {len(df)} rekordów")
    
    # 3. Feature engineering (przed lowercasem!)
    print("\nFeature engineering...")
    df = add_text_features(df)
    
    # 4. Czyszczenie tekstu (po feature engineering)
    df["text_clean"] = df["text"].apply(clean_text)
    
    # 5. Zapis
    output_path = os.path.join(processed_dir, "halueval_unified.csv")
    df.to_csv(output_path, index=False)
    print(f"\nZapisano: {output_path}")
    
    # Podsumowanie
    print("\n" + "=" * 60)
    print("PODSUMOWANIE PO PREPROCESSINGU")
    print("=" * 60)
    print(f"  Rekordów:  {len(df)}")
    print(f"  Kolumn:    {len(df.columns)}")
    print(f"  Kolumny:   {list(df.columns)}")
    print(f"\n  Rozkład labeli:")
    print(f"    0 (poprawne):    {(df['label']==0).sum():>6,} ({(df['label']==0).mean()*100:.1f}%)")
    print(f"    1 (halucynacje): {(df['label']==1).sum():>6,} ({(df['label']==1).mean()*100:.1f}%)")
    print(f"\n  Rozkład źródeł:")
    for src, count in df["source"].value_counts().items():
        print(f"    {src:20s}: {count:>6,}")
    
    return df


# ============================================================
# URUCHOMIENIE STANDALONE
# ============================================================

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(project_root, "data", "raw")
    processed_dir = os.path.join(project_root, "data", "processed")

    df = preprocess_pipeline(raw_dir, processed_dir)

    print("\n[OK] Preprocessing zakonczony!")
    print("   Nastepny krok: python notebooks/01_eda.py")