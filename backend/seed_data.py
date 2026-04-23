"""
Database seeder for the Learning Path Recommendation System.

Generates and inserts synthetic data:
  - 200 students with diverse skills/interests
  - 75 courses across 10 categories
  - ~3000 ratings with affinity-based distributions

Run directly:  python seed_data.py
Or called from main.py on first startup.
"""

import sys
import os
import json
import random

# Add parent directory to path so we can import ml_model
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, User, Course, Rating, init_db
from auth import hash_password
from ml_model.dataset import generate_courses, generate_students, generate_ratings


def seed_database():
    """Populate the database with synthetic data."""
    init_db()
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"Database already has {existing_users} users. Skipping seed.")
            return

        print("=" * 60)
        print("  Seeding Database with Synthetic Data")
        print("=" * 60)

        # ── Generate courses ─────────────────────────────────────────
        print("\n[1/3] Generating 75 courses...")
        course_defs = generate_courses()
        db_courses = []
        for i, c in enumerate(course_defs):
            course = Course(
                id=i + 1,
                name=c["name"],
                category=c["category"],
                difficulty=c["difficulty"],
                description=c["description"],
                skills_covered=json.dumps(c["skills_covered"]),
            )
            db.add(course)
            db_courses.append(c)
        db.flush()
        print(f"   [OK] Created {len(course_defs)} courses")

        # ── Generate students ────────────────────────────────────────
        print("\n[2/3] Generating 200 students...")
        student_defs = generate_students(n_students=200)
        default_password = hash_password("password123")

        for i, s in enumerate(student_defs):
            user = User(
                id=i + 1,
                username=s["username"],
                email=s["email"],
                hashed_password=default_password,
                skills=json.dumps(s["skills"]),
                interests=json.dumps(s["interests"]),
            )
            db.add(user)
        db.flush()
        print(f"   [OK] Created {len(student_defs)} students")

        # ── Generate ratings ─────────────────────────────────────────
        print("\n[3/3] Generating ratings...")
        rating_defs = generate_ratings(student_defs, course_defs, target_ratings=3000)

        for r in rating_defs:
            rating = Rating(
                user_id=r["student_idx"] + 1,   # 1-indexed in DB
                course_id=r["course_idx"] + 1,   # 1-indexed in DB
                rating=r["rating"],
            )
            db.add(rating)

        db.commit()
        print(f"   [OK] Created {len(rating_defs)} ratings")

        print("\n" + "=" * 60)
        print(f"  Seeding complete!")
        print(f"  Students: {len(student_defs)}")
        print(f"  Courses:  {len(course_defs)}")
        print(f"  Ratings:  {len(rating_defs)}")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
