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


MONTH_CHOICES = [
    (1, "Styczeń"), (2, "Luty"), (3, "Marzec"),
    (4, "Kwiecień"), (5, "Maj"), (6, "Czerwiec"),
    (7, "Lipiec"), (8, "Sierpień"), (9, "Wrzesień"),
    (10, "Październik"), (11, "Listopad"), (12, "Grudzień"),
]


class SynastryForm(FlaskForm):
    """Formularz synastrii — dane dwóch osób."""

    # Osoba 1
    name1 = StringField("Imię (osoba 1)", validators=[DataRequired()])
    day1 = IntegerField("Dzień", validators=[InputRequired(), NumberRange(min=1, max=31)])
    month1 = SelectField("Miesiąc", choices=MONTH_CHOICES, coerce=int, validators=[InputRequired()])
    year1 = IntegerField("Rok", validators=[InputRequired(), NumberRange(min=1900, max=2025)])
    hour1 = IntegerField("Godzina", validators=[InputRequired(), NumberRange(min=0, max=23)])
    minute1 = IntegerField("Minuta", validators=[InputRequired(), NumberRange(min=0, max=59)])
    city1 = StringField("Miasto urodzenia", validators=[DataRequired()])

    # Osoba 2
    name2 = StringField("Imię (osoba 2)", validators=[DataRequired()])
    day2 = IntegerField("Dzień", validators=[InputRequired(), NumberRange(min=1, max=31)])
    month2 = SelectField("Miesiąc", choices=MONTH_CHOICES, coerce=int, validators=[InputRequired()])
    year2 = IntegerField("Rok", validators=[InputRequired(), NumberRange(min=1900, max=2025)])
    hour2 = IntegerField("Godzina", validators=[InputRequired(), NumberRange(min=0, max=23)])
    minute2 = IntegerField("Minuta", validators=[InputRequired(), NumberRange(min=0, max=59)])
    city2 = StringField("Miasto urodzenia", validators=[DataRequired()])

    submit = SubmitField("Porównaj charty")