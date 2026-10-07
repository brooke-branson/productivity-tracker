from pydantic import BaseModel, Field
from datetime import datetime

from app.db.models.task_model import Category, FocusLevel, TaskStatus

class TaskCreate(BaseModel):
    name: str = Field(default=None,min_length=3, max_length=255)


class TaskUpdate(BaseModel):
    name: str | None = None
    category: Category | None = None
    status: TaskStatus | None = None
    time_spent_minutes: int | None = Field(default=None, ge=0)
    focus_level: FocusLevel | None = None
    started_at: datetime | None = None

class TaskResponse(BaseModel):
    id: int
    name: str
    category: Category
    status: TaskStatus
    time_spent_minutes: int | None
    focus_level: FocusLevel | None
    created_at: datetime
    started_at: datetime | None
    updated_at: datetime
    completed_at: datetime | None

    model_config = {
        "from_attributes": True
    }