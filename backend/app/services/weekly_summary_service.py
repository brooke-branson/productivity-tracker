from sqlalchemy import select

from app.db.models.task_model import Task, TaskStatus
from app.schemas.task_schema import TaskResponse

from datetime import datetime, timedelta
def calc_weekly_metrics(db, week_start_date: datetime):

    ## Normalizing the week start date to be at the start of the day.

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