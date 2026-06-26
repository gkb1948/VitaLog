from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.user import HealthLog
from datetime import date, timedelta

health = Blueprint("health", __name__)


# ── Daily Log — GET shows form, POST saves entry ─────────────────────────────
@health.route("/log", methods=["GET", "POST"])
@login_required
def log():
    today = date.today()

    # Check if already logged today
    existing = HealthLog.query.filter_by(
        student_id=current_user.id, date=today
    ).first()

    if request.method == "POST":
        water = int(request.form.get("water", 0))
        sleep = float(request.form.get("sleep", 0))
        mood  = request.form.get("mood", "okay")

        # Validate ranges
        if not (0 <= water <= 15):
            flash("Water intake must be between 0 and 15 glasses.", "danger")
            return redirect(url_for("health.log"))
        if not (0 <= sleep <= 12):
            flash("Sleep hours must be between 0 and 12.", "danger")
            return redirect(url_for("health.log"))
        if mood not in ("happy", "okay", "sad"):
            flash("Invalid mood value.", "danger")
            return redirect(url_for("health.log"))

        if existing:
            # Update today's entry
            existing.water = water
            existing.sleep = sleep
            existing.mood  = mood
            flash("Today's health log updated! ✅", "success")
        else:
            # Create new entry
            log_entry = HealthLog(
                student_id=current_user.id,
                date=today,
                water=water,
                sleep=sleep,
                mood=mood
            )
            db.session.add(log_entry)
            flash("Today's health log saved! ✅", "success")

        db.session.commit()
        return redirect(url_for("auth.dashboard"))

    return render_template("health/log.html", today=today, existing=existing)


# ── API: last 7 days data for Chart.js ───────────────────────────────────────
@health.route("/api/weekly")
@login_required
def weekly_data():
    today = date.today()
    days  = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    logs_by_date = {
        log.date: log
        for log in HealthLog.query.filter(
            HealthLog.student_id == current_user.id,
            HealthLog.date >= days[0]
        ).all()
    }

    labels = [d.strftime("%a %d") for d in days]
    water  = [logs_by_date[d].water if d in logs_by_date else None for d in days]
    sleep  = [logs_by_date[d].sleep if d in logs_by_date else None for d in days]
    mood_map = {"happy": 3, "okay": 2, "sad": 1}
    mood   = [mood_map.get(logs_by_date[d].mood, None) if d in logs_by_date else None for d in days]

    return jsonify({"labels": labels, "water": water, "sleep": sleep, "mood": mood})
