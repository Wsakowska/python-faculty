from datetime import datetime
from flask import (
    Blueprint, render_template, request, flash,
    redirect, url_for, session,
)
from app.model_loader import predict

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

    result = predict(text)

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
