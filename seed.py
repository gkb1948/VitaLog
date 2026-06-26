"""
seed.py — Populate VitaLog with realistic student test data.

Run:       python seed.py
Reset DB:  python seed.py --reset

Creates 12 students across 2 Delhi schools (govt + private),
Classes 6-12, with 14 days of health logs each.
Four health profiles to test every part of the dashboard.
"""

import sys
import random
from datetime import date, timedelta

from app import create_app, db
from models.user import Student, HealthLog

app = create_app()

# ── Schools ───────────────────────────────────────────────────────────────────
SCHOOLS = [
    "Govt Sr Sec School Najafgarh",
    "Delhi Public School Dwarka",
]

# ── Students ──────────────────────────────────────────────────────────────────
# (name, email, password, school_index, grade, profile)
# profile: "healthy" | "average" | "attention" | "irregular"
STUDENTS = [
    # Govt school — 7 students
    ("Ananya Sharma",   "ananya@gmail.com",    "pass123", 0, "Class 9",  "healthy"),
    ("Rohan Verma",     "rohan@gmail.com",     "pass123", 0, "Class 10", "average"),
    ("Priya Singh",     "priya@gmail.com",     "pass123", 0, "Class 8",  "attention"),
    ("Aarav Gupta",     "aarav@gmail.com",     "pass123", 0, "Class 11", "healthy"),
    ("Sakshi Yadav",    "sakshi@gmail.com",    "pass123", 0, "Class 7",  "irregular"),
    ("Mohammed Raza",   "mraza@gmail.com",     "pass123", 0, "Class 12", "average"),
    ("Kavya Nair",      "kavya@gmail.com",     "pass123", 0, "Class 6",  "attention"),
    # Private school — 5 students
    ("Arjun Mehta",     "arjun@gmail.com",     "pass123", 1, "Class 10", "healthy"),
    ("Divya Malhotra",  "divya@gmail.com",     "pass123", 1, "Class 9",  "average"),
    ("Siddharth Bose",  "siddharth@gmail.com", "pass123", 1, "Class 11", "irregular"),
    ("Nisha Rawat",     "nisha@gmail.com",     "pass123", 1, "Class 8",  "attention"),
    ("Karan Joshi",     "karan@gmail.com",     "pass123", 1, "Class 12", "healthy"),
]


def log_for_profile(profile, day_index):
    """Return (water, sleep, mood) for a profile on a given day. None = skipped."""
    r = random.Random(profile + str(day_index))

    if profile == "healthy":
        return (
            r.randint(8, 12),
            round(r.uniform(8.0, 10.0), 1),
            r.choices(["happy", "okay"], weights=[7, 3])[0],
        )
    if profile == "average":
        return (
            r.randint(5, 9),
            round(r.uniform(6.5, 9.0), 1),
            r.choices(["happy", "okay", "sad"], weights=[3, 4, 2])[0],
        )
    if profile == "attention":
        return (
            r.randint(2, 5),
            round(r.uniform(4.5, 6.5), 1),
            r.choices(["okay", "sad"], weights=[3, 6])[0],
        )
    if profile == "irregular":
        if r.random() < 0.4:
            return None          # skips ~40% of days
        return (
            r.randint(4, 10),
            round(r.uniform(6.0, 9.5), 1),
            r.choices(["happy", "okay", "sad"], weights=[3, 4, 2])[0],
        )
    return (6, 7.0, "okay")


def seed():
    with app.app_context():

        if "--reset" in sys.argv:
            print("🗑  Resetting database...")
            db.drop_all()
            db.create_all()
            print("✅ Fresh database created\n")
        else:
            db.create_all()

        today = date.today()

        print("── Creating students ────────────────────────────")
        total_logs = 0

        for name, email, pw, school_idx, grade, profile in STUDENTS:
            if Student.query.filter_by(email=email).first():
                print(f"   ⚠️  Already exists: {email}")
                continue

            s = Student(
                name=name, email=email,
                school=SCHOOLS[school_idx], grade=grade,
            )
            s.set_password(pw)
            db.session.add(s)
            db.session.flush()

            log_count = 0
            for offset in range(13, -1, -1):
                result = log_for_profile(profile, offset)
                if result is None:
                    continue
                water, sleep, mood = result
                db.session.add(HealthLog(
                    student_id=s.id,
                    date=today - timedelta(days=offset),
                    water=water, sleep=sleep, mood=mood,
                ))
                log_count  += 1
                total_logs += 1

            icon = {"healthy":"🟢","average":"🟡",
                    "attention":"🔴","irregular":"🔵"}[profile]
            print(f"   {icon} {name:20s} | {grade:8s} | "
                  f"{SCHOOLS[school_idx][:28]:28s} | {log_count} logs")

        db.session.commit()

        print(f"""
══════════════════════════════════════════════════
  ✅ Seed complete
══════════════════════════════════════════════════
  Students : {Student.query.count()}
  Log rows : {HealthLog.query.count()}

  ── Login credentials (password: pass123) ──────

  🟢 HEALTHY  → ananya@gmail.com   (Govt, Class 9)
  🟢 HEALTHY  → arjun@gmail.com    (Private, Class 10)
  🟡 AVERAGE  → rohan@gmail.com    (Govt, Class 10)
  🔴 ATTENTION→ priya@gmail.com    (Govt, Class 8)
  🔴 ATTENTION→ nisha@gmail.com    (Private, Class 8)
  🔵 IRREGULAR→ sakshi@gmail.com   (Govt, Class 7)

  ── Run ────────────────────────────────────────
  python app.py  →  http://127.0.0.1:5000
══════════════════════════════════════════════════
""")


if __name__ == "__main__":
    seed()
