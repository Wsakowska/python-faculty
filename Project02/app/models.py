from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class User(UserMixin, db.Model):
    """Model użytkownika z obsługą ról (user/admin)."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacja — charty użytkownika
    charts = db.relationship("BirthChart", backref="owner", lazy="dynamic",
                             cascade="all, delete-orphan")

    def set_password(self, password):
        """Hashuje i zapisuje hasło."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Sprawdza hasło z hashem."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class BirthChart(db.Model):
    """Model zapisanego chartu urodzeniowego."""

    __tablename__ = "birth_charts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_time = db.Column(db.Time, nullable=False)
    birth_city = db.Column(db.String(200), nullable=False)
    birth_country = db.Column(db.String(100), nullable=False, default="Poland")

    # Wyniki obliczeń — zapisane jako tekst
    sun_sign = db.Column(db.String(30))
    moon_sign = db.Column(db.String(30))
    ascendant = db.Column(db.String(30))
    chart_data = db.Column(db.Text)  # JSON z pełnymi danymi planet

    # Metadane
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    # Klucz obcy — właściciel chartu
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<BirthChart {self.name} ({self.sun_sign})>"


@login_manager.user_loader
def load_user(user_id):
    """Ładuje użytkownika po ID dla Flask-Login."""
    return User.query.get(int(user_id))