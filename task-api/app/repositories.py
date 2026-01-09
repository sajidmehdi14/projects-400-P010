from typing import List, Optional
from sqlmodel import Session, select
from datetime import datetime, timezone
from app.models import Task, TaskCreate, TaskUpdate


class TaskRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, task_data: TaskCreate) -> Task:
        task = Task.model_validate(task_data)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def get_all(self) -> List[Task]:
        statement = select(Task)
        results = self.session.exec(statement)
        return results.all()

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self.session.get(Task, task_id)

    def update(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        task = self.session.get(Task, task_id)
        if not task:
            return None

        task_dict = task_data.model_dump(exclude_unset=True)
        for key, value in task_dict.items():
            setattr(task, key, value)

        task.updated_at = datetime.now(timezone.utc)
        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete(self, task_id: int) -> bool:
        task = self.session.get(Task, task_id)
        if not task:
            return False

        self.session.delete(task)
        self.session.commit()
        return True
