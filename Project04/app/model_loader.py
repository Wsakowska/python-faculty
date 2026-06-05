"""
Ladowanie modelu ML i preprocessing tekstu.
Odtwarza pipeline z Project03: czyszczenie -> TF-IDF -> cechy numeryczne -> predykcja.
"""

import os
import re
import string
import pickle
import numpy as np
from scipy.sparse import hstack, csr_matrix


# Sciezka do katalogu z modelem
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")

# Cache — model i vectorizer ladowane raz
_model = None
_vectorizer = None


def load_model():
    """Laduje model MLP i TF-IDF vectorizer z plikow .pkl."""
    global _model, _vectorizer

    if _model is None:
        model_path = os.path.join(MODEL_DIR, "mlp.pkl")
        with open(model_path, "rb") as f:
            _model = pickle.load(f)

    if _vectorizer is None:
        vec_path = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
        with open(vec_path, "rb") as f:
            _vectorizer = pickle.load(f)

    return _model, _vectorizer


def clean_text(text):
    """
    Czyszczenie tekstu — identyczne jak w Project03 (preprocessing.py).
    """
    if not isinstance(text, str):
        return ""
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.lower()
    return text


def extract_numeric_features(text):
    """
    Ekstrakcja 10 cech numerycznych — identyczne jak w Project03.
    Kolejnosc musi byc taka sama jak przy treningu:
    text_len, word_count, avg_word_len, sentence_count,
    exclamation_count, question_mark_count, uppercase_ratio,
    unique_word_ratio, digit_count, punctuation_ratio
    """
    if not isinstance(text, str) or len(text) == 0:
        return [0] * 10

    words = text.split()
    word_count = len(words)

    features = [
        len(text),                                                      # text_len
        word_count,                                                     # word_count
        np.mean([len(w) for w in words]) if word_count > 0 else 0,      # avg_word_len
        len(re.findall(r'[.!?]+', text)),                               # sentence_count
        text.count("!"),                                                # exclamation_count
        text.count("?"),                                                # question_mark_count
        sum(1 for c in text if c.isupper()) / max(len(text), 1),        # uppercase_ratio
        len(set(text.lower().split())) / max(word_count, 1),            # unique_word_ratio
        sum(1 for c in text if c.isdigit()),                            # digit_count
        sum(1 for c in text if c in string.punctuation) / max(len(text), 1),  # punctuation_ratio
    ]

    return features


def predict(text):
    """
    Pelna predykcja: tekst -> wynik.

    Args:
        text: surowy tekst do sprawdzenia

    Returns:
        dict z kluczami:
            - label: 0 (poprawna) lub 1 (halucynacja)
            - confidence: pewnosc modelu (0.0 - 1.0)
            - label_name: "Poprawna odpowiedz" lub "Halucynacja"
    """
    model, vectorizer = load_model()

    # 1. Cechy numeryczne (przed czyszczeniem — uppercase_ratio potrzebuje oryginalnego tekstu)
    numeric = extract_numeric_features(text)

    # 2. Czyszczenie tekstu
    text_clean = clean_text(text)

    # 3. TF-IDF
    tfidf = vectorizer.transform([text_clean])

    # 4. Polaczenie cech (tak jak w Project03: hstack TF-IDF + numeryczne)
    numeric_sparse = csr_matrix([numeric], dtype=np.float64)
    features = hstack([tfidf, numeric_sparse])

    # 5. Predykcja
    label = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0]
    confidence = float(probabilities[label])

    label_names = {0: "Poprawna odpowiedz", 1: "Halucynacja"}

    return {
        "label": label,
        "confidence": confidence,
        "label_name": label_names[label],
    }
