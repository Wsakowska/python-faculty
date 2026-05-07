"""
01_eda.py — Exploratory Data Analysis
=======================================
project03: Detekcja halucynacji w odpowiedziach LLM

Uruchom po preprocessingu:
    python src/preprocessing.py
    python notebooks/01_eda.py

Generuje wykresy w results/figures/
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# Sciezki
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

PROCESSED_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "halueval_unified.csv")
FIGURES_DIR = os.path.join(PROJECT_ROOT, "results", "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# Styl wykresow
plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
plt.rcParams.update({
    "figure.figsize": (12, 6),
    "font.size": 12,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
})

LABEL_NAMES = {0: "Poprawna", 1: "Halucynacja"}


def save_fig(name: str):
    """Zapisz wykres do results/figures/"""
    path = os.path.join(FIGURES_DIR, f"{name}.png")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Zapisano: {path}")


# ============================================================
# LADOWANIE DANYCH
# ============================================================
print("Ladowanie danych po preprocessingu...")
df = pd.read_csv(PROCESSED_PATH)
print(f"   {len(df)} rekordow, {len(df.columns)} kolumn\n")


# ============================================================
# 1. ROZKLAD LABELI (ogolny)
# ============================================================
print("1. Rozklad labeli...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Pie chart
label_counts = df["label"].value_counts()
axes[0].pie(
    label_counts.values,
    labels=[LABEL_NAMES[i] for i in label_counts.index],
    autopct="%1.1f%%",
    colors=["#2ecc71", "#e74c3c"],
    startangle=90,
    textprops={"fontsize": 13},
)
axes[0].set_title("Rozklad labeli - ogolny")

# Bar chart per source
source_label = df.groupby(["source", "label"]).size().unstack(fill_value=0)
source_label.columns = [LABEL_NAMES[c] for c in source_label.columns]
source_label.plot(kind="bar", ax=axes[1], color=["#2ecc71", "#e74c3c"], edgecolor="white")
axes[1].set_title("Rozklad labeli - per subset")
axes[1].set_xlabel("Subset")
axes[1].set_ylabel("Liczba rekordow")
axes[1].tick_params(axis="x", rotation=0)
axes[1].legend(title="Label")

plt.tight_layout()
save_fig("01_label_distribution")


# ============================================================
# 2. ROZKLAD DLUGOSCI TEKSTU
# ============================================================
print("2. Rozklad dlugosci tekstu...")

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram - word count per label
for label_val in [0, 1]:
    subset = df[df["label"] == label_val]
    axes[0].hist(
        subset["word_count"].clip(upper=500),
        bins=50,
        alpha=0.6,
        label=LABEL_NAMES[label_val],
        color="#2ecc71" if label_val == 0 else "#e74c3c",
    )
axes[0].set_title("Rozklad liczby slow")
axes[0].set_xlabel("Liczba slow (obciete do 500)")
axes[0].set_ylabel("Czestotliwosc")
axes[0].legend()

# Boxplot - word count per source i label
sns.boxplot(
    data=df[df["word_count"] < 500],
    x="source",
    y="word_count",
    hue="label",
    ax=axes[1],
    palette={0: "#2ecc71", 1: "#e74c3c"},
)
axes[1].set_title("Liczba slow - per subset i label")
axes[1].set_xlabel("Subset")
axes[1].set_ylabel("Liczba slow")
handles, labels = axes[1].get_legend_handles_labels()
axes[1].legend(handles, [LABEL_NAMES[int(float(l))] for l in labels], title="Label")

plt.tight_layout()
save_fig("02_text_length_distribution")


# ============================================================
# 3. STATYSTYKI CECH NUMERYCZNYCH
# ============================================================
print("3. Porownanie cech numerycznych...")

feature_cols = [
    "text_len", "word_count", "avg_word_len", "sentence_count",
    "exclamation_count", "question_mark_count", "uppercase_ratio",
    "unique_word_ratio", "digit_count", "punctuation_ratio",
]

# Tabela statystyk per label
stats = df.groupby("label")[feature_cols].agg(["mean", "median", "std"])
print("\nSrednie wartosci cech:")
for feat in feature_cols:
    mean_0 = df[df["label"] == 0][feat].mean()
    mean_1 = df[df["label"] == 1][feat].mean()
    diff_pct = ((mean_1 - mean_0) / max(mean_0, 0.001)) * 100
    marker = "[+]" if diff_pct > 5 else ("[-]" if diff_pct < -5 else "[=]")
    print(f"  {feat:25s}  poprawne={mean_0:8.3f}  halucynacje={mean_1:8.3f}  {marker} {diff_pct:+.1f}%")


# ============================================================
# 4. HEATMAPA KORELACJI CECH
# ============================================================
print("\n4. Heatmapa korelacji...")

fig, ax = plt.subplots(figsize=(10, 8))
corr = df[feature_cols + ["label"]].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr,
    mask=mask,
    annot=True,
    fmt=".2f",
    cmap="RdBu_r",
    center=0,
    ax=ax,
    square=True,
    linewidths=0.5,
)
ax.set_title("Korelacja cech z labelem")
plt.tight_layout()
save_fig("03_feature_correlation")


# ============================================================
# 5. VIOLIN PLOTS - KLUCZOWE CECHY
# ============================================================
print("5. Violin plots kluczowych cech...")

key_features = ["word_count", "avg_word_len", "unique_word_ratio", "punctuation_ratio"]

fig, axes = plt.subplots(1, len(key_features), figsize=(16, 5))
for i, feat in enumerate(key_features):
    data_plot = df.copy()
    # Clip outliers dla czytelnosci
    q99 = data_plot[feat].quantile(0.99)
    data_plot[feat] = data_plot[feat].clip(upper=q99)

    sns.violinplot(
        data=data_plot,
        x="label",
        y=feat,
        hue="label",
        ax=axes[i],
        palette=["#2ecc71", "#e74c3c"],
        inner="quartile",
        legend=False,
    )
    axes[i].set_xticklabels([LABEL_NAMES[0], LABEL_NAMES[1]])
    axes[i].set_title(feat)
    axes[i].set_xlabel("")

plt.suptitle("Rozklad kluczowych cech vs label", fontsize=14, y=1.02)
plt.tight_layout()
save_fig("04_violin_key_features")


# ============================================================
# 6. TOP SLOWA - POPRAWNE VS HALUCYNACJE
# ============================================================
print("6. Najczestsze slowa...")

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

def get_top_words(texts, n=20):
    """Zwraca n najczestszych slow (bez stop words)."""
    words = []
    for text in texts.dropna():
        words.extend([
            w.lower().strip(".,!?;:'\"()[]{}")
            for w in str(text).split()
            if w.lower() not in ENGLISH_STOP_WORDS and len(w) > 2
        ])
    return Counter(words).most_common(n)

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

for idx, label_val in enumerate([0, 1]):
    subset_texts = df[df["label"] == label_val]["text_clean"]
    top = get_top_words(subset_texts, n=20)
    words, counts = zip(*top)

    color = "#2ecc71" if label_val == 0 else "#e74c3c"
    axes[idx].barh(range(len(words)), counts, color=color, edgecolor="white")
    axes[idx].set_yticks(range(len(words)))
    axes[idx].set_yticklabels(words)
    axes[idx].invert_yaxis()
    axes[idx].set_title(f"Top 20 slow - {LABEL_NAMES[label_val]}")
    axes[idx].set_xlabel("Czestotliwosc")

plt.tight_layout()
save_fig("05_top_words")


# ============================================================
# 7. PODSUMOWANIE
# ============================================================
print("\n" + "=" * 60)
print("EDA ZAKONCZONA")
print("=" * 60)
print(f"   Wygenerowano wykresy w: {FIGURES_DIR}/")
print(f"   Pliki:")
for f in sorted(os.listdir(FIGURES_DIR)):
    if f.endswith(".png"):
        print(f"     - {f}")
print(f"\n   Nastepny krok: trenowanie modeli (src/models.py)")