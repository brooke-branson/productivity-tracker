from sqlalchemy import select

from app.db.models.task_model import Task
from datetime import date, timedelta
def generate_weekly_summary(db, week_start_date: date):
    ## Set week end date to be 7 days after start date. Can possibly adjust this later and make weeks be static like Monday-Sunday, that way if a week starts on a Tuesday, the end date is still sunday.
    week_end_date = week_start_date + timedelta(days=7)
    next_week_start_date = week_end_date + timedelta(days=1)

    ## Get all tasks created between start and end date. < next_week_start_date because we want to include the tasks created on the end date, so setting the end date to be the next week start date is exclusive, leaving retrived tasks only in the questioned week.
    tasks = db.scalars(
        select(Task).where(Task.created_at >= week_start_date, Task.created_at < next_week_start_date)
    )