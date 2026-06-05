from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index():
    """Strona glowna z formularzem."""
    return render_template("index.html")
