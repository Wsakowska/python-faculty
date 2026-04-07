from datetime import date, time
from flask import render_template, redirect, url_for, flash, session
from flask_login import current_user, login_required
from app.charts import bp
from app.charts.forms import BirthDataForm
from app.charts.astro_service import generate_chart, chart_data_to_json
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

        # Zapisz dane w sesji, żeby wyświetlić wynik
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
