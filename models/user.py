from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Student(UserMixin, db.Model):
    __tablename__ = "student"

    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    password   = db.Column(db.String(200), nullable=False)
    school     = db.Column(db.String(150), nullable=False)
    grade      = db.Column(db.String(20),  nullable=False)   # e.g. "Class 8"
    logs       = db.relationship("HealthLog", backref="student", lazy=True)

    def set_password(self, raw_password):
        """Hash and store the password — never store plain text."""
        self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        """Check a plain-text password against the stored hash."""
        return check_password_hash(self.password, raw_password)

    def __repr__(self):
        return f"<Student {self.name} | {self.school}>"


class HealthLog(db.Model):
    __tablename__ = "health_log"

    id          = db.Column(db.Integer, primary_key=True)
    student_id  = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    date        = db.Column(db.Date,    nullable=False)
    water       = db.Column(db.Integer, default=0)    # glasses (0-15)
    sleep       = db.Column(db.Float,   default=0.0)  # hours (0-12)
    mood        = db.Column(db.String(20), default="okay")  # happy / okay / sad

    def __repr__(self):
        return f"<HealthLog {self.date} | student {self.student_id}>"
