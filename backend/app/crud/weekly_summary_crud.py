from app.crud.utilities import add_item, remove_item, get_item

from sqlalchemy import select
from sqlalchemy.sql import func
from typing import Optional
from datetime import date, timedelta
from app.db.models.weekly_summ_model import WeeklySummary

def save_weekly_summary(db, weekly_summary: WeeklySummary) -> WeeklySummary:
    existing_weekly_summary = db.scalar(select(WeeklySummary).where(WeeklySummary.week_start_date == weekly_summary.week_start_date))

    if existing_weekly_summary:
        existing_weekly_summary.week_end_date = weekly_summary.week_end_date
        existing_weekly_summary.total_tasks_created = weekly_summary.total_tasks_created
        existing_weekly_summary.total_tasks_started = weekly_summary.total_tasks_started
        existing_weekly_summary.total_tasks_completed = weekly_summary.total_tasks_completed
        existing_weekly_summary.total_time_spent_minutes = weekly_summary.total_time_spent_minutes
        existing_weekly_summary.average_focus_level = weekly_summary.average_focus_level
        existing_weekly_summary.category_distribution = weekly_summary.category_distribution
        existing_weekly_summary.weekly_summary_notes = weekly_summary.weekly_summary_notes
        existing_weekly_summary.weekly_summary_suggestions = weekly_summary.weekly_summary_suggestions
        existing_weekly_summary.related_tasks = weekly_summary.related_tasks

        db.commit()
        db.refresh(existing_weekly_summary)

        return existing_weekly_summary
    else:
        return add_item(db, weekly_summary) 

def get_weekly_summary(db, requested_date: date) -> Optional[WeeklySummary]:
    return db.scalar(select(WeeklySummary).where(
        WeeklySummary.week_start_date <= requested_date,
         WeeklySummary.week_end_date >= requested_date
         )
         )