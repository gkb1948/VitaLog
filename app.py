import os
from flask import Flask
from extensions import db, login_manager


def create_app():
    app = Flask(__name__)

    # ── Config ──────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fallback-dev-only-key")

    raw_uri = os.environ.get("DATABASE_URL", "sqlite:///vitalog.db")
    raw_uri = raw_uri.replace("postgres://", "postgresql://", 1)
    if "postgresql" in raw_uri and "sslmode" not in raw_uri:
        sep = "&" if "?" in raw_uri else "?"
        raw_uri += f"{sep}sslmode=require"
    app.config["SQLALCHEMY_DATABASE_URI"] = raw_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ── Extensions ──────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view             = "auth.login"
    login_manager.login_message          = "Please log in to access VitaLog."
    login_manager.login_message_category = "info"
    login_manager.session_protection     = "strong"

    # ── Import models AFTER init_app ─────────────────────────
    from models.user import Student, HealthLog  # noqa: F401

    # ── User loader ──────────────────────────────────────────
    @login_manager.user_loader
    def load_student(user_id):
        return Student.query.get(int(user_id))

    # ── Blueprints ───────────────────────────────────────────
    from routes.auth   import auth
    from routes.health import health
    app.register_blueprint(auth)
    app.register_blueprint(health)

    # ── Create tables ────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
