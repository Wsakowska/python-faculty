from datetime import date, time
from flask import render_template, redirect, url_for, flash, session, Response
from flask_login import current_user, login_required
from app.charts import bp
from app.charts.forms import BirthDataForm, SynastryForm
from app.charts.astro_service import (
    generate_chart, generate_chart_svg, generate_synastry_svg,
    chart_data_to_json,
)
from app.extensions import db
from app.models import BirthChart


@bp.route("/generate", methods=["GET", "POST"])
def generate():
    """Formularz generowania chartu urodzeniowego."""
    form = BirthDataForm()
    if form.validate_on_submit():
        chart_data = generate_chart(
            name=form.name.data,
            year=form.year.data,
            month=form.month.data,
            day=form.day.data,
            hour=form.hour.data,
            minute=form.minute.data,
            city=form.city.data,
        )

        if chart_data is None:
            flash(
                "Nie udało się wygenerować chartu. Sprawdź, czy miasto jest poprawne "
                "(obsługiwane są polskie miasta).",
                "danger",
            )
            return render_template("charts/generate.html", form=form)

        # Zapisz dane w sesji (tylko lekkie dane, bez SVG)
        session["chart_data"] = chart_data
        session["birth_info"] = {
            "name": form.name.data,
            "day": form.day.data,
            "month": form.month.data,
            "year": form.year.data,
            "hour": form.hour.data,
            "minute": form.minute.data,
            "city": form.city.data,
        }

        return redirect(url_for("charts.result"))

    return render_template("charts/generate.html", form=form)


@bp.route("/result")
def result():
    """Wynik wygenerowanego chartu."""
    chart_data = session.get("chart_data")
    birth_info = session.get("birth_info")

    if not chart_data:
        flash("Najpierw wygeneruj chart.", "warning")
        return redirect(url_for("charts.generate"))

    return render_template(
        "charts/result.html",
        chart=chart_data,
        birth=birth_info,
    )


@bp.route("/svg")
def chart_svg():
    """Generuje SVG mapy urodzeniowej na żądanie (ładowane przez <img> lub <object>)."""
    birth_info = session.get("birth_info")
    if not birth_info:
        return Response("Brak danych", status=404)

    svg = generate_chart_svg(
        name=birth_info["name"],
        year=birth_info["year"],
        month=birth_info["month"],
        day=birth_info["day"],
        hour=birth_info["hour"],
        minute=birth_info["minute"],
        city=birth_info["city"],
    )

    if svg is None:
        return Response("Błąd generowania SVG", status=500)

    return Response(svg, mimetype="image/svg+xml")


@bp.route("/save", methods=["POST"])
@login_required
def save():
    """Zapisuje wygenerowany chart do bazy danych."""
    chart_data = session.get("chart_data")
    birth_info = session.get("birth_info")

    if not chart_data or not birth_info:
        flash("Brak chartu do zapisania.", "warning")
        return redirect(url_for("charts.generate"))

    birth_chart = BirthChart(
        name=birth_info["name"],
        birth_date=date(birth_info["year"], birth_info["month"], birth_info["day"]),
        birth_time=time(birth_info["hour"], birth_info["minute"]),
        birth_city=birth_info["city"],
        sun_sign=chart_data["sun_sign"],
        moon_sign=chart_data["moon_sign"],
        ascendant=chart_data["ascendant"],
        chart_data=chart_data_to_json(chart_data),
        user_id=current_user.id,
    )
    db.session.add(birth_chart)
    db.session.commit()

    flash(f"Chart dla {birth_info['name']} został zapisany!", "success")
    return redirect(url_for("auth.profile"))


@bp.route("/synastry", methods=["GET", "POST"])
def synastry():
    """Formularz synastrii — porównanie dwóch map urodzeniowych."""
    form = SynastryForm()
    if form.validate_on_submit():
        chart1 = generate_chart(
            form.name1.data, form.year1.data, form.month1.data,
            form.day1.data, form.hour1.data, form.minute1.data,
            form.city1.data,
        )
        chart2 = generate_chart(
            form.name2.data, form.year2.data, form.month2.data,
            form.day2.data, form.hour2.data, form.minute2.data,
            form.city2.data,
        )

        if chart1 is None or chart2 is None:
            flash("Nie udało się wygenerować chartów. Sprawdź nazwy miast.", "danger")
            return render_template("charts/synastry.html", form=form)

        session["synastry_data"] = {
            "chart1": chart1,
            "chart2": chart2,
            "birth1": {
                "name": form.name1.data, "day": form.day1.data,
                "month": form.month1.data, "year": form.year1.data,
                "hour": form.hour1.data, "minute": form.minute1.data,
                "city": form.city1.data,
            },
            "birth2": {
                "name": form.name2.data, "day": form.day2.data,
                "month": form.month2.data, "year": form.year2.data,
                "hour": form.hour2.data, "minute": form.minute2.data,
                "city": form.city2.data,
            },
        }

        return redirect(url_for("charts.synastry_result"))

    return render_template("charts/synastry.html", form=form)


@bp.route("/synastry/result")
def synastry_result():
    """Wynik synastrii."""
    data = session.get("synastry_data")
    if not data:
        flash("Najpierw wypełnij formularz synastrii.", "warning")
        return redirect(url_for("charts.synastry"))

    return render_template(
        "charts/synastry_result.html",
        chart1=data["chart1"],
        chart2=data["chart2"],
        birth1=data["birth1"],
        birth2=data["birth2"],
    )


@bp.route("/synastry/svg")
def synastry_svg():
    """Generuje SVG synastrii na żądanie."""
    data = session.get("synastry_data")
    if not data:
        return Response("Brak danych", status=404)

    b1 = data["birth1"]
    b2 = data["birth2"]
    svg = generate_synastry_svg(
        b1["name"], b1["year"], b1["month"], b1["day"], b1["hour"], b1["minute"], b1["city"],
        b2["name"], b2["year"], b2["month"], b2["day"], b2["hour"], b2["minute"], b2["city"],
    )

    if svg is None:
        return Response("Błąd generowania SVG", status=500)

    return Response(svg, mimetype="image/svg+xml")