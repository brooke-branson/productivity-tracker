from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, String, func, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


## Went ahead and defined some initial task statuses ahead, open to change based on feedback.
class TaskStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"

class Category(str, Enum):
    PERSONAL = "personal"
    WORK = "work"
    LEARNING = "learning"
    FITNESS = "fitness"
    OTHER = "other"
    UNCATEGORIZED = "uncategorized"

class FocusLevel(int, Enum):
    VERY_LOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERY_HIGH = 5

class Task(Base):
    """Model for the task table.

        Fields:
        - id: int
        - name: str
        - category: str
        - status: str
        - time_spent_minutes: int | None
        - focus_level: int | None
        - created_at: datetime
        - updated_at: datetime
        - completed_at: datetime | None

    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer,
     primary_key=True,
     )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        )

    category: Mapped[str] = mapped_column(
        String(255),
        nullable=False, 
        default=Category.UNCATEGORIZED.value ## Defaulting to uncategorized as the initial value, and can be updated when task is completed or whenever user want to change.
        )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TaskStatus.PLANNED.value ## Similar to the category, I set the default value to the planned enum, but this is open to change based on feedback.
        )

    time_spent_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        )

    focus_level: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
        onupdate=func.now()
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
    
