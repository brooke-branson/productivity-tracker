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
    
    related tasks: {weekly_summary.related_tasks}
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

def search_weekly_summaries_vectors(query: str, n_results: int = 3) -> list[dict]:
    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    matches = []

    # This loop trims all the unnecessary data and only returns the weekly summary id, week start date, week end date, and distance.
    for metadata, distance in zip(results["metadatas"][0], results["distances"][0]):
        matches.append({
            "weekly_summary_id": metadata.get("weekly_summary_id", None),
            "week_start_date": metadata.get("week_start_date", None),
            "week_end_date": metadata.get("week_end_date", None),
            "distance": distance,
        })

    return matches