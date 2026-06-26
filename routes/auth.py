from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import Student

auth = Blueprint("auth", __name__)


# ── Home ────────────────────────────────────────────────────────────────────
@auth.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return render_template("index.html")


# ── Register ────────────────────────────────────────────────────────────────
@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        name   = request.form.get("name",   "").strip()
        email  = request.form.get("email",  "").strip().lower()
        school = request.form.get("school", "").strip()
        grade  = request.form.get("grade",  "").strip()
        pw     = request.form.get("password", "")
        pw2    = request.form.get("confirm_password", "")

        # ── Validation ──────────────────────────────────────
        errors = []
        if not name:
            errors.append("Name is required.")
        if not email or "@" not in email:
            errors.append("Enter a valid email address.")
        if not school:
            errors.append("School name is required.")
        if not grade:
            errors.append("Grade / class is required.")
        if len(pw) < 6:
            errors.append("Password must be at least 6 characters.")
        if pw != pw2:
            errors.append("Passwords do not match.")
        if Student.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "danger")
            # Re-render with filled values so user doesn't retype everything
            return render_template("auth/register.html",
                                   name=name, email=email,
                                   school=school, grade=grade)

        # ── Create student ──────────────────────────────────
        student = Student(name=name, email=email, school=school, grade=grade)
        student.set_password(pw)
        db.session.add(student)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# ── Login ────────────────────────────────────────────────────────────────────
@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        email    = request.form.get("email",    "").strip().lower()
        pw       = request.form.get("password", "")
        remember = request.form.get("remember") == "on"

        student = Student.query.filter_by(email=email).first()

        if not student or not student.check_password(pw):
            flash("Incorrect email or password. Please try again.", "danger")
            # Pass role="student" so the tab stays on Student after error
            return render_template("auth/login.html", email=email, role="student")

        login_user(student, remember=remember)
        flash(f"Welcome back, {student.name}!", "success")

        next_page = request.args.get("next")
        return redirect(next_page or url_for("auth.dashboard"))

    return render_template("auth/login.html", role="student")


# ── Logout ───────────────────────────────────────────────────────────────────
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


# ── Dashboard ────────────────────────────────────────────────────────────────
@auth.route("/dashboard")
@login_required
def dashboard():
    from models.user import HealthLog
    from datetime import date, timedelta
    import random

    today = date.today()

    # Today's log (may be None)
    today_log = HealthLog.query.filter_by(
        student_id=current_user.id, date=today
    ).first()

    # Streak — count consecutive logged days ending today
    streak = 0
    check_date = today
    while True:
        entry = HealthLog.query.filter_by(
            student_id=current_user.id, date=check_date
        ).first()
        if entry:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    tips = [
        "Drink a glass of water first thing in the morning before checking your phone.",
        "A 20-minute walk after school improves focus and reduces stress.",
        "Eating seasonal fruits like amla and guava boosts immunity during Delhi winters.",
        "Put your phone away 30 minutes before sleeping for better sleep quality.",
        "Deep breathing for 5 minutes can reduce anxiety before exams.",
        "Eating a proper breakfast improves concentration during morning classes.",
        "Washing hands frequently prevents spread of common infections in school.",
    ]
    tip = random.choice(tips)

    return render_template("dashboard.html",
                           today_log=today_log,
                           streak=streak,
                           tip=tip)
