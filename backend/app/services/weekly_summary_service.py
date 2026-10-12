from sqlalchemy import select
from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv
from app.db.models.task_model import Task, TaskStatus
from app.db.models.weekly_summ_model import WeeklySummary
from app.crud.weekly_summary_crud import save_weekly_summary
from app.schemas.task_schema import TaskResponse
from app.schemas.weekly_summary_schema import GeneratedWeeklySummary, WeeklySummaryResponse
from datetime import datetime, timedelta
from app.crud.utilities import get_item
from app.services.vector_store_service import upsert_weekly_summary_vector, search_weekly_summaries_vectors
load_dotenv()

def calc_weekly_metrics(db, week_start_date: datetime):

    ## The route passes a date. Accept a string too, then pin the window to midnight.
    if isinstance(week_start_date, str):
        week_start_date = datetime.strptime(week_start_date, "%Y-%m-%d")
    elif not isinstance(week_start_date, datetime):
        week_start_date = datetime.combine(week_start_date, datetime.min.time())

    week_start_date = week_start_date.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )
    ## Set week end date to be 7 days after start date. Can possibly adjust this later and make weeks be static like Monday-Sunday, that way if a week starts on a Tuesday, the end date is still sunday.
    week_end_date = week_start_date + timedelta(days=6)
    next_week_start_date = week_start_date + timedelta(days=7)

    ## Get all tasks created between start and end date. < next_week_start_date because we want to include the tasks created on the end date, so setting the end date to be the next week start date is exclusive, leaving retrived tasks only in the questioned week.
    created_tasks = db.scalars(
        select(Task).where(Task.created_at >= week_start_date, Task.created_at < next_week_start_date)
    ).all()

    ## There is a small edge case here where started_tasks will only contribute time to tasks started during the week provided, however completed tasks can have time overlapping into the next week. If a task was started 2 weeks ago and has had time dedicated to it, but was completed this week with additional time added, the time will be counted for the previous week. This can be fixed with some sort of versioning system or tracking the time spent on a task across multiple weeks, but I don't think that is in scope right now and will accept that tradeoff.
    started_tasks = db.scalars(
        select(Task).where(Task.started_at >= week_start_date, Task.started_at < next_week_start_date)
    ).all()

    completed_tasks = db.scalars(
        select(Task).where(Task.completed_at >= week_start_date, Task.completed_at < next_week_start_date)
    ).all()

    active_in_progress_tasks = [
        task
        for task in started_tasks
        if task.status == TaskStatus.IN_PROGRESS
    ]

    worked_tasks = active_in_progress_tasks + completed_tasks

    ## Calculate total tasks created, started (meaning set to in-progress), and completed.
    total_tasks_created = len(created_tasks)
    total_tasks_started = len(started_tasks)
    total_tasks_completed = len(completed_tasks)

    serialized_tasks = serialize_tasks(started_tasks + completed_tasks + created_tasks)


    time_spent_in_prog = sum(task.time_spent_minutes for task in started_tasks if task.time_spent_minutes and task.status == TaskStatus.IN_PROGRESS)
    time_spent_completed = sum(task.time_spent_minutes for task in completed_tasks if task.time_spent_minutes and task.status == TaskStatus.COMPLETED)
    total_time_spent_minutes = time_spent_in_prog + time_spent_completed


    focus_levels = [
        task.focus_level for task in completed_tasks if task.focus_level is not None
    ]
    total_focus_level = sum(focus_levels)
    average_focus_level = total_focus_level / len(focus_levels) if focus_levels else None

    return {
        "week_start_date": week_start_date,
        "week_end_date": week_end_date,
        "task_activity": {
            "created": total_tasks_created,
            "started": total_tasks_started,
            "completed": total_tasks_completed,
        },
        "time_spent": {
            "in_progress": time_spent_in_prog,
            "completed": time_spent_completed,
            "total": total_time_spent_minutes,
        },
        "focus_level_completed_tasks": {
            "average": average_focus_level,
        },
        "category_breakdown": {
            "task_counts": calculate_category_breakdown(worked_tasks),
            "avg_completed_focus_level": calculate_avg_focus_level(completed_tasks),
            "total_time_spent": calculate_total_time_spent(worked_tasks),
        },
        "relevant_tasks": serialized_tasks,

    }

def serialize_tasks(tasks: list[Task]) -> list[dict]:
    unique_tasks = {
        task.id: task
        for task in tasks
    }.values()

    serialized_tasks = [
    TaskResponse.model_validate(task).model_dump(
        mode="json",
        exclude={"created_at", "updated_at"},
    )
    for task in unique_tasks
]

    return serialized_tasks

def calculate_category_breakdown(tasks: list[Task]) -> dict:
    category_breakdown = {
            "work": 0,
            "learning": 0,
            "personal": 0,
            "fitness": 0,
            "other": 0,
            "uncategorized": 0,
        }

    for task in tasks:
        category_breakdown[task.category] += 1

    return category_breakdown

def calculate_avg_focus_level(tasks: list[Task]) -> dict:
    avg_focus_level_count = {
        "work": [0,0],
        "learning": [0,0],
        "personal": [0,0],
        "fitness": [0,0],
        "other": [0,0],
        "uncategorized": [0,0],
    }
    for task in tasks:
        if task.focus_level is None:
            continue

        avg_focus_level_count[task.category][0] += task.focus_level
        avg_focus_level_count[task.category][1] += 1

    avg_focus_level = {}

    for category, values in avg_focus_level_count.items():
        total_focus, count = values

        avg_focus_level[category] = (
            total_focus / count
            if count > 0
            else None
        )
    return avg_focus_level

def calculate_total_time_spent(tasks: list[Task]) -> dict:
    total_time_spent = {
        "work": 0,
        "learning": 0,
        "personal": 0,
        "fitness": 0,
        "other": 0,
        "uncategorized": 0,
    }
    for task in tasks:
        total_time_spent[task.category] += task.time_spent_minutes or 0

    return total_time_spent

def generate_weekly_summary(db, weekly_metrics: dict) -> WeeklySummary:
    prompt = """
        Analyze the provided weekly productivity data.

        Generate:
        - summary: one concise paragraph describing productivity, workload,
        completion activity, time distribution, and focus trends.
        - suggestions: 2-4 specific and actionable suggestions based only on
        the provided data.

        Rules:
        - Do not invent activity or context not present in the data.
        - Do not make assumptions about the user's health, priorities, or goals.
        - Tasks with the same id represent the same task and must not be double-counted.
        - A task may appear in relevant_tasks because it was created, started,
        or completed during the selected week.
        - Use the aggregate metrics as the source of truth for weekly totals.
    """
    client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))


    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=[
            types.Part.from_text(text=prompt),
            types.Part.from_text(text=json.dumps(weekly_metrics, default=str)),
        ],    
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GeneratedWeeklySummary,
        ),
    )
    generated_weekly_summary = GeneratedWeeklySummary.model_validate_json(response.text)

    weekly_summary = WeeklySummary(
        week_start_date=weekly_metrics["week_start_date"].date(),
        week_end_date=weekly_metrics["week_end_date"].date(),
        total_tasks_created=weekly_metrics["task_activity"]["created"],
        total_tasks_started=weekly_metrics["task_activity"]["started"],
        total_tasks_completed=weekly_metrics["task_activity"]["completed"],
        total_time_spent_minutes=weekly_metrics["time_spent"]["total"],
        average_focus_level=weekly_metrics["focus_level_completed_tasks"]["average"],
        category_distribution=weekly_metrics["category_breakdown"]["task_counts"],
        weekly_summary_notes=generated_weekly_summary.summary,
        weekly_summary_suggestions=generated_weekly_summary.suggestions,
        related_tasks=[
            {
                "id": task["id"],
                "name": task["name"],
                "category": task["category"],
                "status": task["status"],
            }
            for task in weekly_metrics["relevant_tasks"]
        ],
    )


    saved_weekly_summary = save_weekly_summary(db, weekly_summary)
    ## Upsert the weekly summary to the vector store.
    upsert_weekly_summary_vector(saved_weekly_summary)
    print(f"Weekly summary {saved_weekly_summary.id} upserted to vector store.")
    return saved_weekly_summary

def get_weekly_summary_by_id(db, weekly_summary_id: int) -> WeeklySummary:
    return get_item(db, WeeklySummary, weekly_summary_id, WeeklySummaryResponse)

def get_ranked_weekly_summaries(db, query: str, n_results: int = 3) -> list[WeeklySummary]:
    results = search_weekly_summaries_vectors(query, n_results)

    summary_ids = [
        match["weekly_summary_id"] for match in results
    ]

    summaries = db.scalars(
        select(WeeklySummary).where(WeeklySummary.id.in_(summary_ids))
    ).all()

    # This is a dictionary of the summaries by id, so we can easily access the summary by id later.
    summaries_by_id = {
        summary.id: summary for summary in summaries
    }

    # This list comprehension returns the summaries in the order of the summary ids by ranking from the vector store.
    return [
        summaries_by_id[summary_id] for summary_id in summary_ids if summary_id in summaries_by_id
    ]