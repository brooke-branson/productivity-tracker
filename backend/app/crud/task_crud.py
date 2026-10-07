from app.db.models.task_model import Task
from app.crud.utilities import add_item

from app.schemas.task_schema import TaskCreate

from sqlalchemy import select


def create_task(db, task_create: TaskCreate) -> Task:
    task = Task(
        name=task_create.name,
    )

    return add_item(db, task)
