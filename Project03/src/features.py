"""
Feature extraction
===================
project03: Detekcja halucynacji w odpowiedziach LLM

Tworzy reprezentacje tekstowe (TF-IDF) i dzieli dane na train/test.
Zapisuje gotowe macierze do data/processed/.
"""

import os
import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from scipy.sparse import hstack, save_npz, load_npz


# ============================================================
# 1. TF-IDF VECTORIZATION
# ============================================================

def build_tfidf(texts, max_features=10000, ngram_range=(1, 2)):
    """
    Buduje macierz TF-IDF z tekstow.

    Args:
        texts: seria/lista tekstow
        max_features: max liczba cech
        ngram_range: zakres n-gramow (domyslnie unigramy + bigramy)

    Returns:
        tfidf_matrix: macierz sparse
        vectorizer: dopasowany TfidfVectorizer
    """
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=3,
        max_df=0.95,
        sublinear_tf=True,
        strip_accents="unicode",
    )

    tfidf_matrix = vectorizer.fit_transform(texts)

    print(f"TF-IDF: {tfidf_matrix.shape[0]} dokumentow x {tfidf_matrix.shape[1]} cech")
    print(f"  ngram_range={ngram_range}, max_features={max_features}")

    return tfidf_matrix, vectorizer


# ============================================================
# 2. LACZENIE CECH
# ============================================================

def combine_features(tfidf_matrix, df, feature_cols):
    """
    Laczy macierz TF-IDF z cechami numerycznymi.

    Args:
        tfidf_matrix: macierz sparse TF-IDF
        df: DataFrame z cechami numerycznymi
        feature_cols: lista nazw kolumn numerycznych

    Returns:
        combined: macierz sparse (TF-IDF + cechy numeryczne)
    """
    from scipy.sparse import csr_matrix

    numeric = csr_matrix(df[feature_cols].values.astype(np.float64))
    combined = hstack([tfidf_matrix, numeric])

    print(f"Polaczone cechy: {combined.shape[1]} "
          f"(TF-IDF: {tfidf_matrix.shape[1]} + numeryczne: {len(feature_cols)})")

    return combined


# ============================================================
# 3. PODZIAL TRAIN / TEST
# ============================================================

def split_data(X, y, test_size=0.2, random_state=42):
    """
    Dzieli dane na zbior treningowy i testowy.
    Stratyfikacja po labelu.
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    print(f"Podzial danych:")
    print(f"  Train: {X_train.shape[0]} ({(1-test_size)*100:.0f}%)")
    print(f"  Test:  {X_test.shape[0]} ({test_size*100:.0f}%)")
    print(f"  Train label balance: 0={sum(y_train==0)}, 1={sum(y_train==1)}")
    print(f"  Test label balance:  0={sum(y_test==0)}, 1={sum(y_test==1)}")

    return X_train, X_test, y_train, y_test


# ============================================================
# 4. ZAPIS / ODCZYT
# ============================================================

def save_features(processed_dir, X_train, X_test, y_train, y_test, vectorizer):
    """Zapisuje macierze i vectorizer do pliku."""
    save_npz(os.path.join(processed_dir, "X_train.npz"), X_train)
    save_npz(os.path.join(processed_dir, "X_test.npz"), X_test)
    np.save(os.path.join(processed_dir, "y_train.npy"), y_train)
    np.save(os.path.join(processed_dir, "y_test.npy"), y_test)

    with open(os.path.join(processed_dir, "tfidf_vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"Zapisano do: {processed_dir}/")


def load_features(processed_dir):
    """Wczytuje zapisane macierze i vectorizer."""
    X_train = load_npz(os.path.join(processed_dir, "X_train.npz"))
    X_test = load_npz(os.path.join(processed_dir, "X_test.npz"))
    y_train = np.load(os.path.join(processed_dir, "y_train.npy"))
    y_test = np.load(os.path.join(processed_dir, "y_test.npy"))

    with open(os.path.join(processed_dir, "tfidf_vectorizer.pkl"), "rb") as f:
        vectorizer = pickle.load(f)

    return X_train, X_test, y_train, y_test, vectorizer


# ============================================================
# URUCHOMIENIE STANDALONE
# ============================================================

NUMERIC_FEATURES = [
    "text_len", "word_count", "avg_word_len", "sentence_count",
    "exclamation_count", "question_mark_count", "uppercase_ratio",
    "unique_word_ratio", "digit_count", "punctuation_ratio",
]


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(project_root, "data", "processed")

    # Wczytaj dane po preprocessingu
    print("Ladowanie danych...")
    df = pd.read_csv(os.path.join(processed_dir, "halueval_unified.csv"))
    print(f"  {len(df)} rekordow\n")

    # TF-IDF
    tfidf_matrix, vectorizer = build_tfidf(df["text_clean"].fillna(""))

    # Polaczenie z cechami numerycznymi
    X = combine_features(tfidf_matrix, df, NUMERIC_FEATURES)
    y = df["label"].values

    # Podzial
    X_train, X_test, y_train, y_test = split_data(X, y)

    # Zapis
    save_features(processed_dir, X_train, X_test, y_train, y_test, vectorizer)

    print("\n[OK] Feature extraction zakonczony!")
    print("   Nastepny krok: python src/models.py")
