import os
import re
import string
import pickle
import numpy as np
from scipy.sparse import hstack, csr_matrix


# Sciezka do katalogu z modelem
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "model")

# Cache — modele i vectorizer ladowane raz
_models = {}
_vectorizer = None

# Nazwy modeli i ich pliki
MODEL_FILES = {
    "MLP": "mlp.pkl",
    "Logistic Regression": "logistic_regression.pkl",
    "Naive Bayes": "naive_bayes.pkl",
    "Linear SVM": "linear_svm.pkl",
    "Random Forest": "random_forest.pkl",
    "XGBoost": "xgboost.pkl",
}

# Nazwy cech numerycznych (kolejnosc jak w Project03)
NUMERIC_FEATURE_NAMES = [
    "text_len", "word_count", "avg_word_len", "sentence_count",
    "exclamation_count", "question_mark_count", "uppercase_ratio",
    "unique_word_ratio", "digit_count", "punctuation_ratio",
]

# Opisowe nazwy cech (do wyswietlania)
FEATURE_LABELS = {
    "text_len": "Dlugosc tekstu (znaki)",
    "word_count": "Liczba slow",
    "avg_word_len": "Srednia dlugosc slowa",
    "sentence_count": "Liczba zdan",
    "exclamation_count": "Wykrzykniki",
    "question_mark_count": "Znaki zapytania",
    "uppercase_ratio": "Udzial wielkich liter",
    "unique_word_ratio": "Udzial unikalnych slow",
    "digit_count": "Liczba cyfr",
    "punctuation_ratio": "Udzial interpunkcji",
}

# Srednie wartosci cech z datasetu HaluEval (przyblizone, z treningu Project03)
# Uzywane do porownania z tekstem uzytkownika
REFERENCE_STATS = {
    "text_len":           {"correct": 185.0, "hallucinated": 195.0},
    "word_count":         {"correct": 35.0,  "hallucinated": 37.0},
    "avg_word_len":       {"correct": 4.8,   "hallucinated": 4.7},
    "sentence_count":     {"correct": 2.5,   "hallucinated": 2.8},
    "exclamation_count":  {"correct": 0.05,  "hallucinated": 0.08},
    "question_mark_count":{"correct": 0.15,  "hallucinated": 0.12},
    "uppercase_ratio":    {"correct": 0.03,  "hallucinated": 0.025},
    "unique_word_ratio":  {"correct": 0.72,  "hallucinated": 0.68},
    "digit_count":        {"correct": 1.8,   "hallucinated": 2.5},
    "punctuation_ratio":  {"correct": 0.06,  "hallucinated": 0.055},
}


def _load_vectorizer():
    """Laduje TF-IDF vectorizer."""
    global _vectorizer
    if _vectorizer is None:
        path = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
        with open(path, "rb") as f:
            _vectorizer = pickle.load(f)
    return _vectorizer


def _load_model(name):
    """Laduje pojedynczy model z cache."""
    if name not in _models:
        path = os.path.join(MODEL_DIR, MODEL_FILES[name])
        with open(path, "rb") as f:
            _models[name] = pickle.load(f)
    return _models[name]


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
    Kolejnosc musi byc taka sama jak przy treningu.
    """
    if not isinstance(text, str) or len(text) == 0:
        return [0] * 10

    words = text.split()
    word_count = len(words)

    features = [
        len(text),
        word_count,
        np.mean([len(w) for w in words]) if word_count > 0 else 0,
        len(re.findall(r'[.!?]+', text)),
        text.count("!"),
        text.count("?"),
        sum(1 for c in text if c.isupper()) / max(len(text), 1),
        len(set(text.lower().split())) / max(word_count, 1),
        sum(1 for c in text if c.isdigit()),
        sum(1 for c in text if c in string.punctuation) / max(len(text), 1),
    ]

    return features


def _prepare_features(text):
    """
    Przygotowuje macierz cech z tekstu (TF-IDF + numeryczne).

    Returns:
        features: macierz sparse gotowa do predykcji
        numeric: lista wartosci cech numerycznych (do analizy)
        text_clean: oczyszczony tekst
    """
    vectorizer = _load_vectorizer()

    numeric = extract_numeric_features(text)
    text_clean = clean_text(text)
    tfidf = vectorizer.transform([text_clean])

    numeric_sparse = csr_matrix([numeric], dtype=np.float64)
    features = hstack([tfidf, numeric_sparse])

    return features, numeric, text_clean, tfidf


def predict(text):
    """
    Predykcja z glownego modelu (MLP).

    Returns:
        dict z label, confidence, label_name
    """
    model = _load_model("MLP")
    features, _, _, _ = _prepare_features(text)

    label = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0]
    confidence = float(probabilities[label])

    label_names = {0: "Poprawna odpowiedz", 1: "Halucynacja"}

    return {
        "label": label,
        "confidence": confidence,
        "label_name": label_names[label],
    }


def predict_all_models(text):
    """
    Uruchamia wszystkie 6 modeli na tym samym tekscie.

    Returns:
        lista dict-ow z wynikami kazdego modelu
    """
    features, _, _, _ = _prepare_features(text)
    label_names = {0: "Poprawna", 1: "Halucynacja"}
    results = []

    for name in MODEL_FILES:
        model = _load_model(name)

        # Naive Bayes wymaga nieujemnych wartosci
        if name == "Naive Bayes":
            feat = features.copy()
            feat[feat < 0] = 0
        else:
            feat = features

        label = int(model.predict(feat)[0])
        proba = model.predict_proba(feat)[0]
        confidence = float(proba[label])

        results.append({
            "name": name,
            "label": label,
            "label_name": label_names[label],
            "confidence": round(confidence * 100, 1),
            "prob_hallucination": round(float(proba[1]) * 100, 1),
        })

    # Glosowanie wiekszosciowe
    votes_hallucination = sum(1 for r in results if r["label"] == 1)
    votes_correct = len(results) - votes_hallucination

    summary = {
        "votes_hallucination": votes_hallucination,
        "votes_correct": votes_correct,
        "consensus": "Halucynacja" if votes_hallucination > votes_correct else "Poprawna",
    }

    return results, summary


def analyze_features(text):
    """
    Analizuje cechy numeryczne tekstu i porownuje z referencyjnymi
    wartosciami z datasetu HaluEval.

    Returns:
        lista dict-ow z nazwa cechy, wartoscia, porownaniem
    """
    numeric = extract_numeric_features(text)
    analysis = []

    for i, feat_name in enumerate(NUMERIC_FEATURE_NAMES):
        value = numeric[i]
        ref = REFERENCE_STATS[feat_name]
        avg_correct = ref["correct"]
        avg_hallucinated = ref["hallucinated"]

        # Ktora klasa jest blizsza?
        dist_correct = abs(value - avg_correct)
        dist_hallucinated = abs(value - avg_hallucinated)

        if dist_correct < dist_hallucinated:
            closer_to = "correct"
        elif dist_hallucinated < dist_correct:
            closer_to = "hallucinated"
        else:
            closer_to = "neutral"

        analysis.append({
            "name": feat_name,
            "label": FEATURE_LABELS[feat_name],
            "value": round(value, 3),
            "avg_correct": avg_correct,
            "avg_hallucinated": avg_hallucinated,
            "closer_to": closer_to,
        })

    return analysis


def get_top_tfidf_words(text, top_n=15):
    """
    Zwraca slowa z tekstu o najwyzszych wagach TF-IDF.
    Pokazuje na co model 'patrzyl' najbardziej.

    Returns:
        lista dict-ow z slowem i waga TF-IDF
    """
    vectorizer = _load_vectorizer()
    text_clean = clean_text(text)
    tfidf = vectorizer.transform([text_clean])

    feature_names = vectorizer.get_feature_names_out()
    tfidf_array = tfidf.toarray().flatten()

    # Indeksy niezerowych wag, posortowane malejaco
    nonzero_indices = tfidf_array.nonzero()[0]
    if len(nonzero_indices) == 0:
        return []

    sorted_indices = nonzero_indices[np.argsort(tfidf_array[nonzero_indices])[::-1]]
    top_indices = sorted_indices[:top_n]

    words = []
    for idx in top_indices:
        words.append({
            "word": feature_names[idx],
            "weight": round(float(tfidf_array[idx]), 4),
        })

    return words
