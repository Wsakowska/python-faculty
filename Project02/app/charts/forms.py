from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange


class BirthDataForm(FlaskForm):
    """Formularz danych urodzeniowych do generowania chartu."""

    name = StringField(
        "Imię",
        validators=[DataRequired()],
    )
    day = IntegerField(
        "Dzień",
        validators=[InputRequired(), NumberRange(min=1, max=31)],
    )
    month = SelectField(
        "Miesiąc",
        choices=[
            (1, "Styczeń"), (2, "Luty"), (3, "Marzec"),
            (4, "Kwiecień"), (5, "Maj"), (6, "Czerwiec"),
            (7, "Lipiec"), (8, "Sierpień"), (9, "Wrzesień"),
            (10, "Październik"), (11, "Listopad"), (12, "Grudzień"),
        ],
        coerce=int,
        validators=[InputRequired()],
    )
    year = IntegerField(
        "Rok",
        validators=[InputRequired(), NumberRange(min=1900, max=2025)],
    )
    hour = IntegerField(
        "Godzina",
        validators=[InputRequired(), NumberRange(min=0, max=23)],
    )
    minute = IntegerField(
        "Minuta",
        validators=[InputRequired(), NumberRange(min=0, max=59)],
    )
    city = StringField(
        "Miasto urodzenia",
        validators=[DataRequired()],
    )
    submit = SubmitField("Wygeneruj chart")
