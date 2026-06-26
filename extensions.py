"""
extensions.py — Flask extensions, no project imports.

Single LoginManager for students only.
Admin panel removed — VitaLog is a student health tracker.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db           = SQLAlchemy()
login_manager = LoginManager()
