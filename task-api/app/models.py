from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


def get_utc_now():
    """Get current UTC time."""
    return datetime.now(timezone.utc)


class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=get_utc_now)
    updated_at: datetime = Field(default_factory=get_utc_now)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TaskResponse(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
