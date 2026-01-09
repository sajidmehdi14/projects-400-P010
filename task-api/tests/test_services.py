"""
Unit tests for the TaskService layer.

These tests verify the business logic layer without directly testing the API endpoints.
"""
import pytest
from sqlmodel import Session

from app.services import TaskService
from app.repositories import TaskRepository
from app.models import TaskCreate, TaskUpdate, Task


class TestTaskServiceCreate:
    """Tests for TaskService.create_task method."""

    def test_create_task_success(self, session: Session, sample_task_data):
        """Test creating a task through service layer."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        task = service.create_task(TaskCreate(**sample_task_data))

        assert task.id is not None
        assert task.title == sample_task_data["title"]
        assert task.description == sample_task_data["description"]
        assert task.completed == sample_task_data["completed"]
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_create_task_minimal(self, session: Session):
        """Test creating a task with minimal data."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        task_data = TaskCreate(title="Minimal Task")
        task = service.create_task(task_data)

        assert task.id is not None
        assert task.title == "Minimal Task"
        assert task.description is None
        assert task.completed is False

    def test_create_multiple_tasks(self, session: Session):
        """Test creating multiple tasks."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        tasks_data = [
            TaskCreate(title="Task 1", description="First"),
            TaskCreate(title="Task 2", description="Second"),
            TaskCreate(title="Task 3", description="Third"),
        ]

        created_tasks = [service.create_task(task_data) for task_data in tasks_data]

        assert len(created_tasks) == 3
        assert all(task.id is not None for task in created_tasks)
        # Verify all have unique IDs
        ids = [task.id for task in created_tasks]
        assert len(ids) == len(set(ids))


class TestTaskServiceGetAll:
    """Tests for TaskService.get_all_tasks method."""

    def test_get_all_tasks_empty(self, session: Session):
        """Test getting all tasks when database is empty."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        tasks = service.get_all_tasks()

        assert tasks == []

    def test_get_all_tasks_single(self, session: Session, sample_task):
        """Test getting all tasks with one task."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        tasks = service.get_all_tasks()

        assert len(tasks) == 1
        assert tasks[0].id == sample_task.id

    def test_get_all_tasks_multiple(self, session: Session, multiple_tasks):
        """Test getting all tasks with multiple tasks."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        tasks = service.get_all_tasks()

        assert len(tasks) == 3
        task_ids = [task.id for task in tasks]
        expected_ids = [task.id for task in multiple_tasks]
        assert set(task_ids) == set(expected_ids)


class TestTaskServiceGetById:
    """Tests for TaskService.get_task method."""

    def test_get_task_by_id_success(self, session: Session, sample_task):
        """Test getting a task by valid ID."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        task = service.get_task(sample_task.id)

        assert task is not None
        assert task.id == sample_task.id
        assert task.title == sample_task.title

    def test_get_task_by_id_not_found(self, session: Session):
        """Test getting a task by non-existent ID."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        task = service.get_task(999)

        assert task is None

    def test_get_task_by_id_negative(self, session: Session):
        """Test getting a task with negative ID."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        task = service.get_task(-1)

        assert task is None


class TestTaskServiceUpdate:
    """Tests for TaskService.update_task method."""

    def test_update_task_title(self, session: Session, sample_task):
        """Test updating task title."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        update_data = TaskUpdate(title="Updated Title")
        updated_task = service.update_task(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.title == "Updated Title"
        assert updated_task.description == sample_task.description
        assert updated_task.completed == sample_task.completed

    def test_update_task_description(self, session: Session, sample_task):
        """Test updating task description."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        update_data = TaskUpdate(description="New Description")
        updated_task = service.update_task(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.description == "New Description"
        assert updated_task.title == sample_task.title

    def test_update_task_completed(self, session: Session, sample_task):
        """Test updating task completed status."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        update_data = TaskUpdate(completed=True)
        updated_task = service.update_task(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.completed is True

    def test_update_task_all_fields(self, session: Session, sample_task):
        """Test updating all task fields."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        update_data = TaskUpdate(
            title="New Title",
            description="New Description",
            completed=True
        )
        updated_task = service.update_task(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.title == "New Title"
        assert updated_task.description == "New Description"
        assert updated_task.completed is True

    def test_update_task_partial(self, session: Session, sample_task):
        """Test partial update (only some fields)."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        original_description = sample_task.description

        update_data = TaskUpdate(completed=True)
        updated_task = service.update_task(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.completed is True
        assert updated_task.description == original_description

    def test_update_task_not_found(self, session: Session):
        """Test updating non-existent task."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        update_data = TaskUpdate(title="Should Fail")
        updated_task = service.update_task(999, update_data)

        assert updated_task is None

    def test_update_task_to_null_description(self, session: Session, sample_task):
        """Test setting description to None."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        update_data = TaskUpdate(description=None)
        updated_task = service.update_task(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.description is None


class TestTaskServiceDelete:
    """Tests for TaskService.delete_task method."""

    def test_delete_task_success(self, session: Session, sample_task):
        """Test deleting a task successfully."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        result = service.delete_task(sample_task.id)

        assert result is True

        # Verify task is deleted
        deleted_task = service.get_task(sample_task.id)
        assert deleted_task is None

    def test_delete_task_not_found(self, session: Session):
        """Test deleting non-existent task."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        result = service.delete_task(999)

        assert result is False

    def test_delete_task_negative_id(self, session: Session):
        """Test deleting task with negative ID."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        result = service.delete_task(-1)

        assert result is False

    def test_delete_multiple_tasks(self, session: Session, multiple_tasks):
        """Test deleting multiple tasks."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        for task in multiple_tasks:
            result = service.delete_task(task.id)
            assert result is True

        # Verify all tasks are deleted
        remaining_tasks = service.get_all_tasks()
        assert len(remaining_tasks) == 0


class TestTaskServiceIntegration:
    """Integration tests for TaskService workflows."""

    def test_create_update_delete_workflow(self, session: Session):
        """Test complete workflow through service layer."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        # Create
        create_data = TaskCreate(
            title="Workflow Test",
            description="Testing workflow",
            completed=False
        )
        task = service.create_task(create_data)
        assert task.id is not None
        task_id = task.id

        # Read
        retrieved_task = service.get_task(task_id)
        assert retrieved_task is not None
        assert retrieved_task.title == "Workflow Test"

        # Update
        update_data = TaskUpdate(completed=True)
        updated_task = service.update_task(task_id, update_data)
        assert updated_task is not None
        assert updated_task.completed is True

        # Delete
        result = service.delete_task(task_id)
        assert result is True

        # Verify deletion
        deleted_task = service.get_task(task_id)
        assert deleted_task is None

    def test_service_maintains_data_integrity(self, session: Session):
        """Test that service layer maintains data integrity."""
        repository = TaskRepository(session)
        service = TaskService(repository)

        # Create task
        task1 = service.create_task(TaskCreate(title="Task 1"))
        task2 = service.create_task(TaskCreate(title="Task 2"))

        # Update task1
        service.update_task(task1.id, TaskUpdate(completed=True))

        # Verify task2 is not affected
        task2_check = service.get_task(task2.id)
        assert task2_check.completed is False

        # Delete task1
        service.delete_task(task1.id)

        # Verify task2 still exists
        task2_final = service.get_task(task2.id)
        assert task2_final is not None
