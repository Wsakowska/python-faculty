"""
Modele ML
==========
project03: Detekcja halucynacji w odpowiedziach LLM

6 modeli:
  1. Logistic Regression (baseline)
  2. Multinomial Naive Bayes
  3. Linear SVM
  4. Random Forest
  5. XGBoost (gradient boosting)
  6. MLP (siec neuronowa)
"""

import os
import time
import pickle
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.calibration import CalibratedClassifierCV

from features import load_features, NUMERIC_FEATURES
from evaluation import (
    set_output_dirs, evaluate_model, plot_confusion_matrix,
    plot_learning_curve, plot_roc_curves, plot_model_comparison,
    save_metrics,
)


# ============================================================
# DEFINICJE MODELI
# ============================================================

def get_models():
    """
    Zwraca slownik modeli do wytrenowania.
    Kazdy model ma inne hiperparametry — roznorodnosc jest wymagana.

    Modele:
      - Logistic Regression: liniowy, regularyzacja L2, szybki baseline
      - Naive Bayes: probabilistyczny, zaklada niezaleznosc cech
      - Linear SVM: liniowy, max-margin, dobry na duze wymiary
      - Random Forest: ensemble drzew, bagging, nieliniowy
      - XGBoost (GradientBoosting): ensemble drzew, boosting, sekwencyjny
      - MLP: siec neuronowa, nieliniowe transformacje, backpropagation
    """
    models = {
        "Logistic Regression": LogisticRegression(
            C=1.0,                  # sila regularyzacji (odwrotnosc)
            solver="lbfgs",         # optymalizator
            max_iter=1000,          # max iteracji
            random_state=42,
            n_jobs=-1,
        ),

        "Naive Bayes": MultinomialNB(
            alpha=0.1,              # wygladzanie Laplace'a
        ),

        "Linear SVM": CalibratedClassifierCV(
            LinearSVC(
                C=1.0,              # parametr regularyzacji
                max_iter=2000,      # max iteracji
                random_state=42,
            ),
            cv=3,                   # kalibracja — potrzebna do predict_proba
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=200,       # liczba drzew
            max_depth=30,           # maks. glebokosc drzewa
            min_samples_split=5,    # min. probek do podzialu
            min_samples_leaf=2,     # min. probek w lisciu
            random_state=42,
            n_jobs=-1,
        ),

        "XGBoost": GradientBoostingClassifier(
            n_estimators=200,       # liczba drzew (boosting rounds)
            learning_rate=0.1,      # tempo uczenia
            max_depth=5,            # glebokosc drzewa (mniejsza niz RF)
            subsample=0.8,          # losowy podzbiur probek
            random_state=42,
        ),

        "MLP": MLPClassifier(
            hidden_layer_sizes=(256, 128),  # 2 warstwy ukryte
            activation="relu",              # funkcja aktywacji
            solver="adam",                  # optymalizator
            learning_rate="adaptive",       # adaptacyjne tempo uczenia
            max_iter=100,                   # max epok
            early_stopping=True,            # zatrzymanie przy braku poprawy
            validation_fraction=0.1,        # czesc danych do walidacji
            random_state=42,
        ),
    }

    return models


# ============================================================
# TRENING I EWALUACJA
# ============================================================

def train_and_evaluate(models, X_train, X_test, y_train, y_test):
    """
    Trenuje wszystkie modele i zbiera wyniki.

    Args:
        models: dict {nazwa: model}
        X_train, X_test, y_train, y_test: dane

    Returns:
        all_metrics: lista dict-ow z metrykami
        roc_data: lista dict-ow z danymi do ROC
    """
    all_metrics = []
    roc_data = []

    for name, model in models.items():
        print(f"\n{'#'*60}")
        print(f"# Trening: {name}")
        print(f"{'#'*60}")

        # Naive Bayes nie obsluguje wartosci ujemnych (TF-IDF sublinear moze dac 0, ale nie ujemne)
        # Na wszelki wypadek obslugujemy to
        X_train_model = X_train
        X_test_model = X_test
        if name == "Naive Bayes":
            # MultinomialNB wymaga nieujemnych wartosci
            X_train_model = X_train.copy()
            X_test_model = X_test.copy()
            X_train_model[X_train_model < 0] = 0
            X_test_model[X_test_model < 0] = 0

        # Trening
        start = time.time()
        model.fit(X_train_model, y_train)
        train_time = time.time() - start
        print(f"  Czas treningu: {train_time:.1f}s")

        # Predykcja prawdopodobienstw (jesli dostepna)
        y_prob = None
        if hasattr(model, "predict_proba"):
            y_prob = model.predict_proba(X_test_model)[:, 1]

        # Ewaluacja
        metrics, y_pred = evaluate_model(model, X_test_model, y_test, name, y_prob)
        metrics["train_time_s"] = round(train_time, 1)
        all_metrics.append(metrics)

        # Macierz bledow
        plot_confusion_matrix(y_test, y_pred, name)

        # Dane do ROC
        roc_data.append({"model": name, "y_prob": y_prob})

        # Zapisz model
        safe_name = name.lower().replace(" ", "_")
        model_path = os.path.join(MODELS_DIR, f"{safe_name}.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        print(f"  Model zapisany: {model_path}")

    return all_metrics, roc_data


# ============================================================
# WYBOR NAJLEPSZEGO MODELU
# ============================================================

def select_best_model(all_metrics):
    """
    Wybiera najlepszy model na podstawie F1 score.
    F1 jest glowna metryka, bo zalezy nam na rownowadze
    precision i recall w detekcji halucynacji.
    """
    import pandas as pd
    df = pd.DataFrame(all_metrics)
    df = df.sort_values("f1", ascending=False)

    best = df.iloc[0]

    print("\n" + "=" * 60)
    print("RANKING MODELI (wg F1)")
    print("=" * 60)
    for i, row in df.iterrows():
        marker = " <-- BEST" if row["model"] == best["model"] else ""
        print(f"  {row['model']:25s}  F1={row['f1']:.4f}  Acc={row['accuracy']:.4f}  "
              f"Time={row['train_time_s']}s{marker}")

    print(f"\nNajlepszy model: {best['model']}")
    print(f"  F1={best['f1']:.4f}, Accuracy={best['accuracy']:.4f}, "
          f"Precision={best['precision']:.4f}, Recall={best['recall']:.4f}")

    return best["model"]


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    processed_dir = os.path.join(project_root, "data", "processed")
    MODELS_DIR = os.path.join(project_root, "models")
    os.makedirs(MODELS_DIR, exist_ok=True)

    figures_dir = os.path.join(project_root, "results", "figures")
    metrics_dir = os.path.join(project_root, "results", "metrics")
    set_output_dirs(figures_dir, metrics_dir)

    # Wczytaj dane
    print("Ladowanie danych...")
    X_train, X_test, y_train, y_test, vectorizer = load_features(processed_dir)
    print(f"  Train: {X_train.shape}, Test: {X_test.shape}\n")

    # Modele
    models = get_models()

    # Trening i ewaluacja
    all_metrics, roc_data = train_and_evaluate(
        models, X_train, X_test, y_train, y_test,
    )

    # Krzywe ROC
    print("\nGenerowanie krzywych ROC...")
    plot_roc_curves(roc_data, y_test)

    # Porownanie modeli
    print("Generowanie porownania modeli...")
    plot_model_comparison(all_metrics)

    # Zapis metryk
    save_metrics(all_metrics)

    # Najlepszy model
    best_name = select_best_model(all_metrics)

    # Krzywa uczenia dla najlepszego modelu
    print(f"\nGenerowanie krzywej uczenia dla: {best_name}...")
    best_model = models[best_name]

    # Dla krzywej uczenia bierzemy mniejszy sample (szybkosc)
    sample_size = min(15000, X_train.shape[0])
    indices = np.random.RandomState(42).choice(X_train.shape[0], sample_size, replace=False)
    X_sample = X_train[indices]
    y_sample = y_train[indices]

    # Naive Bayes — usun ujemne
    if best_name == "Naive Bayes":
        X_sample = X_sample.copy()
        X_sample[X_sample < 0] = 0

    plot_learning_curve(best_model, X_sample, y_sample, best_name)

    print("\n" + "=" * 60)
    print("[OK] Trening i ewaluacja zakonczone!")
    print("=" * 60)
    print(f"  Wykresy:  {figures_dir}/")
    print(f"  Metryki:  {metrics_dir}/model_metrics.csv")
    print(f"  Modele:   {MODELS_DIR}/")
