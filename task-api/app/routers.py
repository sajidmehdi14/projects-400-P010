from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.models import TaskCreate, TaskUpdate, TaskResponse
from app.repositories import TaskRepository
from app.services import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_task_service(session: Session = Depends(get_session)) -> TaskService:
    repository = TaskRepository(session)
    return TaskService(repository)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    service: TaskService = Depends(get_task_service)
):
    return service.create_task(task)


@router.get("", response_model=List[TaskResponse])
def get_tasks(service: TaskService = Depends(get_task_service)):
    return service.get_all_tasks()


@router.get("/{id}", response_model=TaskResponse)
def get_task(
    id: int,
    service: TaskService = Depends(get_task_service)
):
    task = service.get_task(id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task


@router.put("/{id}", response_model=TaskResponse)
def update_task(
    id: int,
    task: TaskUpdate,
    service: TaskService = Depends(get_task_service)
):
    updated_task = service.update_task(id, task)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return updated_task


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    id: int,
    service: TaskService = Depends(get_task_service)
):
    deleted = service.delete_task(id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
