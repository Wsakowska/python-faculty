from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.auth import bp
from app.auth.forms import RegistrationForm, LoginForm
from app.extensions import db
from app.models import User


@bp.route("/register", methods=["GET", "POST"])
def register():
    """Rejestracja nowego użytkownika."""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Konto zostało utworzone! Możesz się teraz zalogować.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Logowanie użytkownika."""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Nieprawidłowa nazwa użytkownika lub hasło.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        flash(f"Witaj, {user.username}!", "success")
        return redirect(next_page or url_for("main.home"))

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    """Wylogowanie użytkownika."""
    logout_user()
    flash("Zostałeś wylogowany.", "info")
    return redirect(url_for("main.home"))


@bp.route("/profile")
@login_required
def profile():
    """Profil zalogowanego użytkownika."""
    charts = current_user.charts.order_by(None).all()
    return render_template("auth/profile.html", charts=charts)
