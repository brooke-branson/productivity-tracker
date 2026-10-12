from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException

from app.db.session import Session, get_db
from app.crud.task_crud import create_task, update_task, list_tasks, get_task, del_task
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from app.schemas.weekly_summary_schema import WeeklySummaryResponse
from app.crud.weekly_summary_crud import get_weekly_summary
from app.db.base import Base
from app.db.session import engine
from datetime import date
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
def generate_weekly_summary_endpoint(week_start_date: date, db: Session = Depends(get_db)):
    ## TODO: Check if weekly summary already exists for the week, if it does, return it.
    ## TODO: Format the week_start_date to be alyways send to the beginning of the week. For example, if the week_start_date is 2026-10-10, the beginning of the week is 2026-10-05. Still deciding on what will be the first day of the week, likely sunday or monday.
    weekly_metrics = calc_weekly_metrics(db, week_start_date)
    return generate_weekly_summary(db, weekly_metrics)

@app.get("/weekly-summary/{week_start_date}", response_model=WeeklySummaryResponse)
def get_weekly_summary_endpoint(week_start_date: date, db: Session = Depends(get_db)):
    weekly_summary = get_weekly_summary(db, week_start_date)
    if not weekly_summary:
        ## This is just placeholder error handling for now. In the future, this would actually work to generate a weekly summary in the background if it didn't exist.
        raise HTTPException(status_code=404, detail="Weekly summary not found")
    return weekly_summary