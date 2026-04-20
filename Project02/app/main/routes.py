from flask import render_template, request
from app.main import bp
from app.models import BirthChart
from app.charts.astro_service import SIGN_NAMES_PL


@bp.route("/")
def home():
    """Strona główna aplikacji."""
    return render_template("main/home.html")


@bp.route("/about")
def about():
    """Informacje o aplikacji."""
    return render_template("main/about.html")


@bp.route("/search")
def search():
    """Wyszukiwarka chartów po imieniu, znaku słonecznym lub mieście."""
    query = request.args.get("q", "").strip()
    results = []

    if query:
        # Szukaj po imieniu, znaku słonecznym, znaku księżyca, ascendencie lub mieście
        search_filter = (
            BirthChart.name.ilike(f"%{query}%")
            | BirthChart.sun_sign.ilike(f"%{query}%")
            | BirthChart.moon_sign.ilike(f"%{query}%")
            | BirthChart.ascendant.ilike(f"%{query}%")
            | BirthChart.birth_city.ilike(f"%{query}%")
        )
        results = BirthChart.query.filter(search_filter).order_by(
            BirthChart.created_at.desc()
        ).limit(50).all()

    # Lista dostępnych znaków do podpowiedzi
    signs = list(SIGN_NAMES_PL.values())

    return render_template(
        "main/search.html",
        query=query,
        results=results,
        signs=signs,
    )