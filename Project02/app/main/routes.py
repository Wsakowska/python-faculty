from flask import render_template
from app.main import bp


@bp.route("/")
def home():
    """Strona główna aplikacji."""
    return render_template("main/home.html")


@bp.route("/about")
def about():
    """Informacje o aplikacji."""
    return render_template("main/about.html")