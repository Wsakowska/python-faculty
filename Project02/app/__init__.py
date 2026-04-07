from flask import Flask, render_template
from config import Config
from app.extensions import db, migrate, login_manager, csrf


def create_app(config_class=Config):
    """Application factory — tworzy i konfiguruje instancję Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicjalizacja rozszerzeń
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Rejestracja blueprintów
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.charts import bp as charts_bp
    app.register_blueprint(charts_bp, url_prefix="/charts")

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # Import modeli, żeby user_loader się zarejestrował
    from app import models  # noqa: F401

    # Obsługa błędów
    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    return app