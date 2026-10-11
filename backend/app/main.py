from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException

from app.db.session import Session, get_db
from app.crud.task_crud import create_task, update_task, list_tasks, get_task, del_task
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.weekly_summary_schema import WeeklySummaryResponse
from app.crud.weekly_summary_crud import get_weekly_summary
from app.db.base import Base
from app.db.session import engine

from app.services.weekly_summary_service import generate_weekly_summary, calc_weekly_metrics
# Base.metadata.drop_all(bind=engine) ## TODO: Remove this in production
Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

## CRUD endpoints for the Task model.
@app.post("/tasks", response_model=TaskResponse)
def create_task_endpoint(task_create: TaskCreate, db: Session = Depends(get_db)):
    task = create_task(db, task_create)
    if not task:
        raise HTTPException(status_code=400, detail="Failed to create task")
    return task

@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task_endpoint(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(status_code=400, detail="Failed to update task")
    return task

@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks_endpoint(db: Session = Depends(get_db)):
    tasks = list_tasks(db)
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    task = get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}", response_model=TaskResponse)
def delete_task_endpoint(task_id: int, db: Session = Depends(get_db)):
    task = del_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

## End of CRUD endpoints for the Task model.

## Weekly summary endpoint.
@app.post("/weekly-summary/{week_start_date}", response_model=WeeklySummaryResponse)
def generate_weekly_summary_endpoint(week_start_date: str, db: Session = Depends(get_db)):
    weekly_metrics = calc_weekly_metrics(db, week_start_date)
    return generate_weekly_summary(db, weekly_metrics)

@app.get("/weekly-summary/{week_start_date}", response_model=WeeklySummaryResponse)
def get_weekly_summary_endpoint(week_start_date: str, db: Session = Depends(get_db)):
    weekly_summary = get_weekly_summary(db, week_start_date)
    if not weekly_summary:
        raise HTTPException(status_code=404, detail="Weekly summary not found")
    return weekly_summary