import os
import sys
from flask import Flask
from extensions import db, login_manager


def create_app():
    app = Flask(__name__)

    # ── Config ──────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "fallback-dev-only-key")

    raw_uri = os.environ.get("DATABASE_URL", "sqlite:///vitalog.db")
    if raw_uri.startswith("postgres://"):
        raw_uri = raw_uri.replace("postgres://", "postgresql://", 1)
    if raw_uri.startswith("postgresql"):
        raw_uri += "&" if "?" in raw_uri else "?"
        raw_uri += "sslmode=require&connect_timeout=10"
    app.config["SQLALCHEMY_DATABASE_URI"] = raw_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    print(f"[boot] DB: {'postgresql' if 'postgresql' in raw_uri else 'sqlite'}", flush=True)
    print(f"[boot] SECRET_KEY set: {bool(app.config['SECRET_KEY'])}", flush=True)

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
        try:
            db.create_all()
            print("[boot] Tables created OK", flush=True)
        except Exception as e:
            print(f"[boot] DB ERROR: {e}", flush=True)
            raise

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
