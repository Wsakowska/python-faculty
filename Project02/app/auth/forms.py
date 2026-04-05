from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import User


class RegistrationForm(FlaskForm):
    """Formularz rejestracji nowego użytkownika."""

    username = StringField(
        "Nazwa użytkownika",
        validators=[DataRequired(), Length(min=3, max=64)]
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()]
    )
    password = PasswordField(
        "Hasło",
        validators=[DataRequired(), Length(min=6)]
    )
    password2 = PasswordField(
        "Powtórz hasło",
        validators=[DataRequired(), EqualTo("password", message="Hasła muszą być takie same.")]
    )
    submit = SubmitField("Zarejestruj się")

    def validate_username(self, username):
        """Sprawdza, czy nazwa użytkownika jest już zajęta."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Ta nazwa użytkownika jest już zajęta.")

    def validate_email(self, email):
        """Sprawdza, czy email jest już w użyciu."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Ten adres email jest już zarejestrowany.")


class LoginForm(FlaskForm):
    """Formularz logowania."""

    username = StringField(
        "Nazwa użytkownika",
        validators=[DataRequired()]
    )
    password = PasswordField(
        "Hasło",
        validators=[DataRequired()]
    )
    remember_me = BooleanField("Zapamiętaj mnie")
    submit = SubmitField("Zaloguj się")
