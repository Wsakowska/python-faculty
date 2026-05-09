"""
Ewaluacja modeli
=================
project03: Detekcja halucynacji w odpowiedziach LLM

Metryki, macierz bledow, krzywe uczenia sie, porownanie modeli.
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve,
)
from sklearn.model_selection import learning_curve


LABEL_NAMES = {0: "Poprawna", 1: "Halucynacja"}
FIGURES_DIR = None
METRICS_DIR = None


def set_output_dirs(figures_dir, metrics_dir):
    """Ustawia katalogi wyjsciowe."""
    global FIGURES_DIR, METRICS_DIR
    FIGURES_DIR = figures_dir
    METRICS_DIR = metrics_dir
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(METRICS_DIR, exist_ok=True)


def evaluate_model(model, X_test, y_test, model_name, y_prob=None):
    """
    Oblicza metryki dla jednego modelu.

    Args:
        model: wytrenowany model (z metoda predict)
        X_test: dane testowe
        y_test: prawdziwe labele
        model_name: nazwa modelu (do wyswietlania)
        y_prob: prawdopodobienstwa klasy pozytywnej (opcjonalne)

    Returns:
        dict z metrykami
    """
    y_pred = model.predict(X_test)

    metrics = {
        "model": model_name,
        "accuracy": accuracy_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
    }

    if y_prob is not None:
        metrics["roc_auc"] = roc_auc_score(y_test, y_prob)
    else:
        metrics["roc_auc"] = None

    print(f"\n{'='*50}")
    print(f"Model: {model_name}")
    print(f"{'='*50}")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  F1:        {metrics['f1']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:    {metrics['recall']:.4f}")
    if metrics["roc_auc"]:
        print(f"  ROC AUC:   {metrics['roc_auc']:.4f}")

    return metrics, y_pred


def plot_confusion_matrix(y_test, y_pred, model_name):
    """Rysuje macierz bledow."""
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=[LABEL_NAMES[0], LABEL_NAMES[1]],
        yticklabels=[LABEL_NAMES[0], LABEL_NAMES[1]],
        ax=ax,
    )
    ax.set_xlabel("Predykcja")
    ax.set_ylabel("Prawdziwy label")
    ax.set_title(f"Macierz bledow - {model_name}")
    plt.tight_layout()

    safe_name = model_name.lower().replace(" ", "_")
    path = os.path.join(FIGURES_DIR, f"cm_{safe_name}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Zapisano: {path}")


def plot_learning_curve(model, X_train, y_train, model_name, cv=5):
    """
    Rysuje krzywa uczenia sie (train vs validation score w funkcji rozmiaru danych).
    """
    train_sizes, train_scores, val_scores = learning_curve(
        model, X_train, y_train,
        cv=cv,
        n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 10),
        scoring="f1",
    )

    train_mean = train_scores.mean(axis=1)
    train_std = train_scores.std(axis=1)
    val_mean = val_scores.mean(axis=1)
    val_std = val_scores.std(axis=1)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.1, color="#2ecc71")
    ax.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.1, color="#e74c3c")
    ax.plot(train_sizes, train_mean, "o-", color="#2ecc71", label="Train F1")
    ax.plot(train_sizes, val_mean, "o-", color="#e74c3c", label="Validation F1")

    ax.set_xlabel("Rozmiar zbioru treningowego")
    ax.set_ylabel("F1 Score")
    ax.set_title(f"Krzywa uczenia - {model_name}")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    safe_name = model_name.lower().replace(" ", "_")
    path = os.path.join(FIGURES_DIR, f"lc_{safe_name}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Zapisano: {path}")


def plot_roc_curves(results_list, y_test):
    """
    Rysuje krzywe ROC dla wszystkich modeli na jednym wykresie.

    Args:
        results_list: lista dict-ow z kluczami 'model', 'y_prob'
        y_test: prawdziwe labele
    """
    fig, ax = plt.subplots(figsize=(8, 6))

    for result in results_list:
        if result["y_prob"] is not None:
            fpr, tpr, _ = roc_curve(y_test, result["y_prob"])
            auc = roc_auc_score(y_test, result["y_prob"])
            ax.plot(fpr, tpr, label=f"{result['model']} (AUC={auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", alpha=0.3, label="Random")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("Krzywe ROC - porownanie modeli")
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    path = os.path.join(FIGURES_DIR, f"roc_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Zapisano: {path}")


def plot_model_comparison(all_metrics):
    """
    Wykres slupkowy porownujacy metryki wszystkich modeli.
    """
    df_metrics = pd.DataFrame(all_metrics)
    metrics_to_plot = ["accuracy", "f1", "precision", "recall"]

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(df_metrics))
    width = 0.2

    for i, metric in enumerate(metrics_to_plot):
        ax.bar(x + i * width, df_metrics[metric], width, label=metric.capitalize())

    ax.set_xticks(x + width * 1.5)
    ax.set_xticklabels(df_metrics["model"], rotation=15, ha="right")
    ax.set_ylabel("Score")
    ax.set_title("Porownanie modeli - metryki")
    ax.legend()
    ax.set_ylim(0.5, 1.0)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()

    path = os.path.join(FIGURES_DIR, "model_comparison.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Zapisano: {path}")


def save_metrics(all_metrics, filename="model_metrics.csv"):
    """Zapisuje metryki do CSV."""
    df = pd.DataFrame(all_metrics)
    path = os.path.join(METRICS_DIR, filename)
    df.to_csv(path, index=False)
    print(f"  Zapisano metryki: {path}")
    return df
