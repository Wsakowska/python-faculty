from flask import Blueprint, render_template, request, flash, redirect, url_for
from app.model_loader import predict

main = Blueprint("main", __name__)

MIN_TEXT_LENGTH = 10


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

    return render_template(
        "result.html",
        text=text,
        label=result["label"],
        confidence=result["confidence"],
        label_name=result["label_name"],
    )


@main.route("/about")
def about():
    """Strona z opisem projektu."""
    return render_template("about.html")
