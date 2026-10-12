from datetime import datetime, date

from sqlalchemy import DateTime, Integer, func, JSON, Date, Text, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class WeeklySummary(Base):
    """
    Model for the weekly_summaries table.

    Fields:
    - id: int

    - week_start_date: date
    - week_end_date: date

    - total_tasks_created: int
    - total_tasks_completed: int
    - total_tasks_started: int
    
    - total_time_spent_minutes: int
    - average_focus_level: float | None
    - category_distribution: dict[str, int]

    - weekly_summary_notes: str | None
    - weekly_summary_suggestions: list[str]
    - related_tasks: list[int]

    - created_at: datetime
    - updated_at: datetime

    """

    __tablename__ = "weekly_summaries"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
        )
    
    week_start_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        unique=True
        )
    
    week_end_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
        )

    total_tasks_created: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
        )
    
    total_tasks_completed: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
        )
    
    total_tasks_started: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
        )

    total_time_spent_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
        )
    
    average_focus_level: Mapped[float | None] = mapped_column(
        Float,
        nullable=True ## Allows for null values if no focus level is set for the week, for any reason, maybe user didn't do anything that week, they just started using the platform, etc...
        )
    
    category_distribution: Mapped[dict[str, int]] = mapped_column(
        JSON,
        nullable=False,
        default=dict
        )
    
    weekly_summary_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
        )

    weekly_summary_suggestions: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list
        )
    related_tasks: Mapped[list[dict]] = mapped_column(
        JSON,
        nullable=False,
        default=list
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