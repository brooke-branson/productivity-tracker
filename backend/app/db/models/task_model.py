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


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer,
     primary_key=True,
     )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        )

    category: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True, ## Set this to nullable for now, may be required when task is completed.
        )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=TaskStatus.PLANNED.value ## Similar to the category, I set the default value to the planned enum, but this is open to change based on feedback.
        )

    time_spent: Mapped[int | None] = mapped_column(
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
    
