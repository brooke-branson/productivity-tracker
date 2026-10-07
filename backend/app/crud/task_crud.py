from app.db.models.task_model import Task, TaskStatus
from app.crud.utilities import add_item, remove_item, get_item

from app.schemas.task_schema import TaskCreate, TaskResponse, TaskUpdate

from sqlalchemy import select
from sqlalchemy.sql import func
"""
    All of the CRUD operations for the Task model. 

    Design choice to break each model into its own file, and the crud operations that can be shared across models into their own file.
"""

def create_task(db, task_create: TaskCreate) -> Task:
    task = Task(
        name=task_create.name,
    )

    return add_item(db, task)

def del_task(db, id: int) -> TaskResponse | None:
    deleted_task = remove_item(db, Task, id, TaskResponse)

    return deleted_task

def get_task(db, id: int) -> TaskResponse | None:
    return get_item(db, Task, id, TaskResponse)

def update_task(db, id: int, edits: TaskUpdate):
    existing_task = db.scalar(
        select(Task).where(Task.id == id)
    )
    if not existing_task:
        return None
    edit_data = edits.model_dump(exclude_unset=True)
    
    ## Actual business logic starts here, validating the edits before the task is updated.
    proposed_status = edit_data.get("status", existing_task.status)
    proposed_time = edit_data.get("time_spent_minutes", existing_task.time_spent_minutes)
    proposed_focus = edit_data.get("focus_level", existing_task.focus_level)

    ## This block is here to validate focus and time if the edit is to complete the task. 
    if proposed_status == TaskStatus.COMPLETED:
        ## The time must be greater than 0 for proper tracking, it's not realistic to have a task with no time spent.
        ## This rule is up to interpretation though, in the event a user forgot to add a task in the past and wants it tracked now, but can discuss this later.
        if proposed_time is None or proposed_time <= 0:
            raise ValueError("Time spent must be greater than 0 when completing a task")

        ## Same as the time, a focus level is required when completing a task.
        if proposed_focus is None:
            raise ValueError("Focus is required when completing a task")

    
    for k, v in edit_data.items():
        setattr(existing_task, k, v)
    
    if (
        proposed_status == TaskStatus.IN_PROGRESS
        and existing_task.started_at is None
    ):
        ## If the task is being started, and it hasn't been started yet, set the started_at time to the current time.
        existing_task.started_at = func.now()

    if (
        proposed_status == TaskStatus.COMPLETED
        and existing_task.completed_at is None
    ):
        ## If the task is being completed, and the complete time has not been set yet, set the completed_at time to the current time.
        ## There is an edge case here to discuss where task is set to completed but it was never set to in progress. First thing that comes to mind is to set the started_at time to the current time if it hasn't been set yet.
        existing_task.completed_at = func.now()
    
    try:
        db.commit()
        db.refresh(existing_task)

        return existing_task

    except Exception:
        db.rollback()
        raise

def list_tasks(db) -> list[Task]:
    tasks = db.scalars(
        select(Task).order_by(Task.created_at.desc())
    ).all()


    return tasks

## TODO: Add additional fetching options to list tasks by various filters, such as status, focus level, time spent, etc...