import chromadb
from app.db.models.weekly_summ_model import WeeklySummary
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_PATH = BASE_DIR / "chroma_data"

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = client.get_or_create_collection(name="weekly_summaries")


def build_weekly_summary_document(weekly_summary: WeeklySummary) -> str:

    return f"""
    week: {weekly_summary.week_start_date} to {weekly_summary.week_end_date}

    tasks created: {weekly_summary.total_tasks_created}
    tasks started: {weekly_summary.total_tasks_started}
    tasks completed: {weekly_summary.total_tasks_completed}

    total time spent: {weekly_summary.total_time_spent_minutes} minutes
    average focus level: {weekly_summary.average_focus_level}

    category distribution: 
    {weekly_summary.category_distribution}

    weekly summary notes: {weekly_summary.weekly_summary_notes}
    weekly summary suggestions: {weekly_summary.weekly_summary_suggestions}

    """ 

def upsert_weekly_summary_vector(weekly_summary: WeeklySummary):
    document = build_weekly_summary_document(weekly_summary)
    collection.upsert(
        ids=[f"weekly-summary-{weekly_summary.id}"],
        documents=[document],
        metadatas=[
            {
                "weekly_summary_id": weekly_summary.id,
                "week_start_date": str(weekly_summary.week_start_date),
                "week_end_date": str(weekly_summary.week_end_date),
            }
        ],
    )