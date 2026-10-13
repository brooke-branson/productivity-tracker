"""
Wipe demo / application data from SQLite and Chroma.

Run after the stack is up:

    docker compose exec backend python -m scripts.clear_seed

Removes all tasks, weekly summaries, and Chroma vector entries.
Does not delete the Docker volumes themselves.
"""

from __future__ import annotations

from app.db.base import Base
from app.db.models.task_model import Task
from app.db.models.weekly_summ_model import WeeklySummary
from app.db.session import SessionLocal, engine
from app.services.vector_store_service import collection


def main() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        removed_summaries = db.query(WeeklySummary).delete()
        removed_tasks = db.query(Task).delete()
        db.commit()
    finally:
        db.close()

    existing = collection.get()
    ids = existing.get("ids") or []
    if ids:
        collection.delete(ids=ids)

    print(
        f"Cleared {removed_tasks} tasks, {removed_summaries} summaries, "
        f"{len(ids)} vectors."
    )


if __name__ == "__main__":
    main()
