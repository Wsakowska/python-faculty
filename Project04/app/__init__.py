from flask import Flask


def create_app():
    """App factory — tworzy i konfiguruje instancje aplikacji Flask."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "halucheck-dev-key"

    from app.routes import main
    app.register_blueprint(main)

    return app