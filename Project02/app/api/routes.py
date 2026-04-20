"""REST API — endpointy JSON do generowania i pobierania chartów."""

from flask import jsonify, request
from flask_login import current_user, login_required
from app.api import bp
from app.charts.astro_service import generate_chart, json_to_chart_data
from app.models import BirthChart


@bp.route("/chart", methods=["POST"])
def api_generate_chart():
    """Generuje chart urodzeniowy i zwraca dane jako JSON.

    Oczekuje JSON body:
    {
        "name": "Wiktoria",
        "year": 2001, "month": 3, "day": 28,
        "hour": 20, "minute": 0,
        "city": "Starogard Gdański"
    }

    Zwraca: JSON z pozycjami planet, znakami i domami.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Brak danych JSON w żądaniu."}), 400

    # Walidacja wymaganych pól
    required = ["name", "year", "month", "day", "hour", "minute", "city"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"Brakujące pola: {', '.join(missing)}"}), 400

    chart_data = generate_chart(
        name=data["name"],
        year=data["year"],
        month=data["month"],
        day=data["day"],
        hour=data["hour"],
        minute=data["minute"],
        city=data["city"],
    )

    if chart_data is None:
        return jsonify({
            "error": "Nie udało się wygenerować chartu. Sprawdź nazwę miasta."
        }), 422

    return jsonify(chart_data), 200


@bp.route("/charts", methods=["GET"])
@login_required
def api_list_charts():
    """Zwraca listę zapisanych chartów zalogowanego użytkownika.

    Zwraca: JSON array z podsumowaniem każdego chartu.
    """
    charts = (
        BirthChart.query
        .filter_by(user_id=current_user.id)
        .order_by(BirthChart.created_at.desc())
        .all()
    )

    result = []
    for chart in charts:
        result.append({
            "id": chart.id,
            "name": chart.name,
            "birth_date": chart.birth_date.isoformat(),
            "birth_time": chart.birth_time.strftime("%H:%M"),
            "birth_city": chart.birth_city,
            "sun_sign": chart.sun_sign,
            "moon_sign": chart.moon_sign,
            "ascendant": chart.ascendant,
            "created_at": chart.created_at.isoformat(),
        })

    return jsonify(result), 200


@bp.route("/charts/<int:chart_id>", methods=["GET"])
@login_required
def api_get_chart(chart_id):
    """Zwraca szczegóły zapisanego chartu (z pełnymi danymi planet).

    Zwraca: JSON z danymi chartu.
    """
    chart = BirthChart.query.get_or_404(chart_id)
    if chart.user_id != current_user.id:
        return jsonify({"error": "Brak dostępu."}), 403

    chart_data = json_to_chart_data(chart.chart_data)

    return jsonify({
        "id": chart.id,
        "name": chart.name,
        "birth_date": chart.birth_date.isoformat(),
        "birth_time": chart.birth_time.strftime("%H:%M"),
        "birth_city": chart.birth_city,
        "sun_sign": chart.sun_sign,
        "moon_sign": chart.moon_sign,
        "ascendant": chart.ascendant,
        "created_at": chart.created_at.isoformat(),
        "planets": chart_data.get("planets", []) if chart_data else [],
    }), 200


@bp.route("/cities", methods=["GET"])
def api_list_cities():
    """Zwraca listę obsługiwanych miast.

    Zwraca: JSON array z nazwami miast.
    """
    from app.charts.astro_service import CITIES_PL
    cities = sorted([city.title() for city in CITIES_PL.keys()])
    return jsonify(cities), 200