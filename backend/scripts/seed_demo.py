"""
Seed demo tasks for local / Docker testing.

Run after the stack is up:

    docker compose exec backend python -m scripts.seed_demo

Creates 100 tasks across the previous 4 complete Sunday–Saturday weeks.
Each week leans hard into one theme (coding, fitness, learning, personal)
so that after you generate weekly summaries through the normal endpoint,
historical search can answer questions like "show me a week where I coded
a lot" or "...fitness".

This script does NOT generate weekly summaries or Chroma vectors.
Use POST /weekly-summary/{week_start_date} (or the UI Generate button)
so Gemini writes the summary and the endpoint indexes it in Chroma.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from random import Random

from app.db.base import Base
from app.db.models.task_model import Task
from app.db.models.weekly_summ_model import WeeklySummary
from app.db.session import SessionLocal, engine
from app.services.vector_store_service import collection

# Fixed seed so every engineer gets the same demo dataset.
RNG = Random(42)
TASKS_PER_WEEK = 25

WEEKS = [
    {
        "theme": "coding",
        "category": "work",
        "names": [
            "Refactor authentication service",
            "Implement task list API endpoints",
            "Debug intermittent Docker networking",
            "Pair program on weekly summary flow",
            "Write integration tests for CRUD",
            "Optimize SQLite query hot path",
            "Ship frontend chart performance fix",
            "Code review pull requests for API",
            "Prototype vector search helper",
            "Fix race condition in task updates",
            "Build seed script for demo data",
            "Implement nginx reverse proxy rules",
            "Rewrite datetime parsing utilities",
            "Add pagination to task board UI",
            "Instrument backend request logging",
            "Migrate schemas for weekly summaries",
            "Harden FastAPI validation errors",
            "Spike chroma document formatting",
            "Finish Dockerfile multi-stage build",
            "Clean up dead code in services",
        ],
    },
    {
        "theme": "fitness",
        "category": "fitness",
        "names": [
            "Morning 5k run",
            "Strength training: legs",
            "Strength training: upper body",
            "Evening mobility session",
            "HIIT interval workout",
            "Long weekend hike",
            "Yoga for recovery",
            "Swim laps at the pool",
            "Core stability circuit",
            "Cycling interval ride",
            "Track tempo run",
            "Deadlift progressive set",
            "Stretch and foam roll",
            "Climbing gym session",
            "Rest-day walk outdoors",
            "Boxing bag intervals",
            "Meal prep for training week",
            "Physio mobility drills",
            "Sprint repeats at the track",
            "Cool-down recovery jog",
        ],
    },
    {
        "theme": "learning",
        "category": "learning",
        "names": [
            "Finish FastAPI advanced course module",
            "Read paper on retrieval-augmented generation",
            "Practice system design flashcards",
            "Watch distributed systems lecture",
            "Work through SQL window-function drills",
            "Study React concurrent rendering notes",
            "Complete algo practice: graphs",
            "Read chapter on embedding models",
            "Take notes on Docker networking",
            "Review Pydantic-AI agent patterns",
            "Sketch architecture for search pipeline",
            "Anki review: networking fundamentals",
            "Watch talk on product discovery",
            "Study Chroma indexing docs",
            "Rewrite notes on HTTP caching",
            "Complete TypeScript utility types lesson",
            "Read RFC summary on OAuth basics",
            "Practice prompt-evaluation checklist",
            "Shadow a design critique recording",
            "Summarize weekly learning in journal",
        ],
    },
    {
        "theme": "personal",
        "category": "personal",
        "names": [
            "Plan weekly family meals",
            "Deep clean kitchen and pantry",
            "Schedule dentist appointment",
            "Organize home office closet",
            "Pay bills and update budget",
            "Grocery run for the week",
            "Help with school project night",
            "Car maintenance appointment",
            "Sort mail and paperwork",
            "Call insurance about claim",
            "Plant herbs on the balcony",
            "Host dinner with friends",
            "Update photo album backups",
            "Declutter spare bedroom",
            "Birthday gift shopping",
            "Laundry and linen refresh",
            "Plan weekend day trip",
            "Write thank-you notes",
            "Review subscriptions and cancel unused",
            "Set up recurring calendar reminders",
        ],
    },
]

FILLER = [
    ("other", "Catch up on email inbox"),
    ("other", "Quick team stand-up notes"),
    ("uncategorized", "Misc follow-up reminder"),
    ("work", "Short status sync"),
    ("personal", "Pick up package"),
]


def sunday_on_or_before(day: date) -> date:
    # Python: Monday=0 … Sunday=6. Shift so Sunday is the week start.
    return day - timedelta(days=(day.weekday() + 1) % 7)


def clear_demo_data(db) -> None:
    # Drop old summaries/vectors too so a reseed does not leave stale
    # Gemini/Chroma state that no longer matches the new tasks.
    removed_summaries = db.query(WeeklySummary).delete()
    removed_tasks = db.query(Task).delete()
    db.commit()

    existing = collection.get()
    ids = existing.get("ids") or []
    if ids:
        collection.delete(ids=ids)

    print(f"Cleared {removed_tasks} tasks, {removed_summaries} summaries, {len(ids)} vectors.")


def build_week_tasks(week_start: date, week_cfg: dict) -> list[Task]:
    theme_names = list(week_cfg["names"])
    RNG.shuffle(theme_names)

    # ~20 themed completed tasks, ~3 filler completed, ~2 planned/in-progress.
    slots: list[tuple[str, str, str]] = []
    for name in theme_names[:20]:
        slots.append((name, week_cfg["category"], "completed"))
    for category, name in FILLER[:3]:
        slots.append((name, category, "completed"))
    slots.append(
        (
            theme_names[20] if len(theme_names) > 20 else "Wrap theme leftovers",
            week_cfg["category"],
            "in-progress",
        )
    )
    slots.append((FILLER[3][1], FILLER[3][0], "planned"))

    tasks: list[Task] = []
    for index, (name, category, status) in enumerate(slots[:TASKS_PER_WEEK]):
        day_offset = index % 7
        hour = 9 + (index % 8)
        created = datetime.combine(
            week_start + timedelta(days=day_offset),
            datetime.min.time(),
        ) + timedelta(hours=hour, minutes=5 * (index % 6))
        started = created + timedelta(minutes=15)
        minutes = RNG.choice([45, 60, 75, 90, 120, 150]) if status != "planned" else None
        focus = (
            RNG.choice([3, 4, 5])
            if status == "completed"
            else (RNG.choice([2, 3, 4]) if status == "in-progress" else None)
        )
        completed = started + timedelta(minutes=minutes or 0) if status == "completed" else None

        # Themed completed work gets longer blocks so charts / metrics look obvious.
        if status == "completed" and category == week_cfg["category"]:
            minutes = RNG.choice([90, 120, 150, 180])
            focus = RNG.choice([4, 5])
            completed = started + timedelta(minutes=minutes)

        tasks.append(
            Task(
                name=name,
                category=category,
                status=status,
                time_spent_minutes=minutes,
                focus_level=focus,
                created_at=created,
                started_at=None if status == "planned" else started,
                updated_at=completed or started or created,
                completed_at=completed,
            )
        )
    return tasks


def main() -> None:
    Base.metadata.create_all(bind=engine)

    current_sunday = sunday_on_or_before(date.today())
    # Previous 4 complete weeks; leave the current week empty for live testing.
    week_starts = [current_sunday - timedelta(weeks=offset) for offset in (4, 3, 2, 1)]

    db = SessionLocal()
    try:
        clear_demo_data(db)

        total_tasks = 0
        for week_start, week_cfg in zip(week_starts, WEEKS):
            week_tasks = build_week_tasks(week_start, week_cfg)
            db.add_all(week_tasks)
            db.commit()
            total_tasks += len(week_tasks)

            end = week_start + timedelta(days=6)
            print(
                f"Week {week_start} – {end}: theme={week_cfg['theme']}, "
                f"tasks={len(week_tasks)}"
            )

        print(f"Seeded {total_tasks} tasks across {len(week_starts)} weeks.")
        print("No weekly summaries were created.")
        print("Generate each week via the UI or:")
        for week_start in week_starts:
            print(f"  POST /weekly-summary/{week_start}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
