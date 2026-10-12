from pydantic import BaseModel
from app.schemas.task_schema import Category, TaskStatus
from datetime import datetime, date

class WeeklySummaryCreate(BaseModel):
    ## Kept create very small and simple here, as backend will handle the rest of the logic. No need to expose to front end unless needed.
    ## The start date is techincally not needed since we get to define what the start date is, but this allows for easy generation of "historical" data for testing purposes.
    week_start_date: date

class RelatedTaskSnapshot(BaseModel):
    id: int
    name: str
    category: Category
    status: TaskStatus

class WeeklySummaryResponse(BaseModel):
    id: int

    week_start_date: date
    week_end_date: date

    total_tasks_created: int
    total_tasks_completed: int
    total_tasks_started: int
    total_time_spent_minutes: int
    average_focus_level: float | None
    category_distribution: dict[str, int]

    weekly_summary_notes: str | None
    weekly_summary_suggestions: list[str] | None
    related_tasks: list[RelatedTaskSnapshot]

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

class GeneratedWeeklySummary(BaseModel):
    summary: str
    suggestions: list[str]