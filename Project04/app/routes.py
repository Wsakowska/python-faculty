from datetime import datetime
from flask import (
    Blueprint, render_template, request, flash,
    redirect, url_for, session,
)
from app.model_loader import predict, predict_all_models, analyze_features, get_top_tfidf_words

main = Blueprint("main", __name__)

MIN_TEXT_LENGTH = 10
MAX_HISTORY = 20


@main.route("/")
def index():
    """Strona glowna z formularzem."""
    return render_template("index.html")


@main.route("/predict", methods=["POST"])
def predict_route():
    """Obsluga formularza — predykcja halucynacji."""
    text = request.form.get("text_input", "").strip()

    if len(text) < MIN_TEXT_LENGTH:
        flash(
            f"Tekst jest za krotki (minimum {MIN_TEXT_LENGTH} znakow).",
            "warning",
        )
        return redirect(url_for("main.index"))

    # Glowna predykcja (MLP)
    result = predict(text)

    # Panel 6 modeli
    model_results, model_summary = predict_all_models(text)

    # Analiza cech
    feature_analysis = analyze_features(text)

    # Top slowa TF-IDF
    top_words = get_top_tfidf_words(text, top_n=15)

    # Zapis do historii w sesji
    entry = {
        "text": text[:200] + ("..." if len(text) > 200 else ""),
        "label": result["label"],
        "label_name": result["label_name"],
        "confidence": round(result["confidence"] * 100, 1),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    history = session.get("history", [])
    history.insert(0, entry)
    session["history"] = history[:MAX_HISTORY]

    return render_template(
        "result.html",
        text=text,
        label=result["label"],
        confidence=result["confidence"],
        label_name=result["label_name"],
        model_results=model_results,
        model_summary=model_summary,
        feature_analysis=feature_analysis,
        top_words=top_words,
    )


@main.route("/history")
def history():
    """Historia zapytan z biezacej sesji."""
    entries = session.get("history", [])
    return render_template("history.html", entries=entries)


@main.route("/history/clear", methods=["POST"])
def clear_history():
    """Czyszczenie historii."""
    session.pop("history", None)
    flash("Historia zostala wyczyszczona.", "info")
    return redirect(url_for("main.history"))


@main.route("/about")
def about():
    """Strona z opisem projektu."""
    return render_template("about.html")
