from flask import Blueprint

bp = Blueprint("charts", __name__, template_folder="templates")

from app.charts import routes  # noqa: E402, F401