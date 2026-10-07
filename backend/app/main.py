from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException

from app.db.session import Session, get_db
from app.db.models.task_model import Task

from app.crud.task_crud import create_task
from app.schemas.task_schema import TaskCreate, TaskUpdate, TaskResponse
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.post("/tasks", response_model=TaskResponse)
def create_task_endpoint(task_create: TaskCreate, db: Session = Depends(get_db)):
    task = create_task(db, task_create)
    if not task:
        raise HTTPException(status_code=400, detail="Failed to create task")
    return task