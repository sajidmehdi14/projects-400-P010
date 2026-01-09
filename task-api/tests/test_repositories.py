"""
Unit tests for the TaskRepository layer.

These tests verify the data access layer functionality.
"""
import pytest
from sqlmodel import Session, select
from datetime import datetime, timezone

from app.repositories import TaskRepository
from app.models import Task, TaskCreate, TaskUpdate


class TestTaskRepositoryCreate:
    """Tests for TaskRepository.create method."""

    def test_create_task(self, session: Session, sample_task_data):
        """Test creating a task in the repository."""
        repository = TaskRepository(session)
        task_data = TaskCreate(**sample_task_data)

        task = repository.create(task_data)

        assert task.id is not None
        assert task.title == sample_task_data["title"]
        assert task.description == sample_task_data["description"]
        assert task.completed == sample_task_data["completed"]
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_create_task_persisted_in_db(self, session: Session):
        """Test that created task is persisted in database."""
        repository = TaskRepository(session)
        task_data = TaskCreate(title="Persisted Task")

        created_task = repository.create(task_data)

        # Query directly from database to verify
        statement = select(Task).where(Task.id == created_task.id)
        db_task = session.exec(statement).first()

        assert db_task is not None
        assert db_task.id == created_task.id
        assert db_task.title == "Persisted Task"

    def test_create_task_auto_increment_id(self, session: Session):
        """Test that task IDs are auto-incremented."""
        repository = TaskRepository(session)

        task1 = repository.create(TaskCreate(title="Task 1"))
        task2 = repository.create(TaskCreate(title="Task 2"))
        task3 = repository.create(TaskCreate(title="Task 3"))

        assert task1.id < task2.id < task3.id

    def test_create_task_timestamps_set(self, session: Session):
        """Test that timestamps are automatically set on creation."""
        repository = TaskRepository(session)
        task_data = TaskCreate(title="Timestamp Test")

        before_create = datetime.now(timezone.utc)
        task = repository.create(task_data)
        after_create = datetime.now(timezone.utc)

        # Convert task timestamps to timezone-aware if they're naive
        task_created_at = task.created_at if task.created_at.tzinfo else task.created_at.replace(tzinfo=timezone.utc)
        task_updated_at = task.updated_at if task.updated_at.tzinfo else task.updated_at.replace(tzinfo=timezone.utc)

        assert before_create <= task_created_at <= after_create
        assert before_create <= task_updated_at <= after_create


class TestTaskRepositoryGetAll:
    """Tests for TaskRepository.get_all method."""

    def test_get_all_empty_database(self, session: Session):
        """Test getting all tasks from empty database."""
        repository = TaskRepository(session)

        tasks = repository.get_all()

        assert tasks == []

    def test_get_all_single_task(self, session: Session, sample_task):
        """Test getting all tasks with one task in database."""
        repository = TaskRepository(session)

        tasks = repository.get_all()

        assert len(tasks) == 1
        assert tasks[0].id == sample_task.id

    def test_get_all_multiple_tasks(self, session: Session, multiple_tasks):
        """Test getting all tasks with multiple tasks in database."""
        repository = TaskRepository(session)

        tasks = repository.get_all()

        assert len(tasks) == 3
        task_ids = [task.id for task in tasks]
        expected_ids = [task.id for task in multiple_tasks]
        assert set(task_ids) == set(expected_ids)

    def test_get_all_returns_task_objects(self, session: Session, sample_task):
        """Test that get_all returns Task objects with all fields."""
        repository = TaskRepository(session)

        tasks = repository.get_all()

        assert len(tasks) == 1
        task = tasks[0]
        assert isinstance(task, Task)
        assert hasattr(task, 'id')
        assert hasattr(task, 'title')
        assert hasattr(task, 'description')
        assert hasattr(task, 'completed')
        assert hasattr(task, 'created_at')
        assert hasattr(task, 'updated_at')


class TestTaskRepositoryGetById:
    """Tests for TaskRepository.get_by_id method."""

    def test_get_by_id_existing_task(self, session: Session, sample_task):
        """Test getting an existing task by ID."""
        repository = TaskRepository(session)

        task = repository.get_by_id(sample_task.id)

        assert task is not None
        assert task.id == sample_task.id
        assert task.title == sample_task.title
        assert task.description == sample_task.description

    def test_get_by_id_nonexistent_task(self, session: Session):
        """Test getting a non-existent task by ID."""
        repository = TaskRepository(session)

        task = repository.get_by_id(999)

        assert task is None

    def test_get_by_id_negative_id(self, session: Session):
        """Test getting task with negative ID."""
        repository = TaskRepository(session)

        task = repository.get_by_id(-1)

        assert task is None

    def test_get_by_id_zero_id(self, session: Session):
        """Test getting task with ID zero."""
        repository = TaskRepository(session)

        task = repository.get_by_id(0)

        assert task is None

    def test_get_by_id_correct_task(self, session: Session, multiple_tasks):
        """Test that get_by_id returns the correct task when multiple exist."""
        repository = TaskRepository(session)

        # Get the second task
        target_task = multiple_tasks[1]
        retrieved_task = repository.get_by_id(target_task.id)

        assert retrieved_task is not None
        assert retrieved_task.id == target_task.id
        assert retrieved_task.title == target_task.title


class TestTaskRepositoryUpdate:
    """Tests for TaskRepository.update method."""

    def test_update_task_title(self, session: Session, sample_task):
        """Test updating task title."""
        repository = TaskRepository(session)
        update_data = TaskUpdate(title="Updated Title")

        updated_task = repository.update(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.title == "Updated Title"
        assert updated_task.description == sample_task.description

    def test_update_task_description(self, session: Session, sample_task):
        """Test updating task description."""
        repository = TaskRepository(session)
        update_data = TaskUpdate(description="Updated Description")

        updated_task = repository.update(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.description == "Updated Description"
        assert updated_task.title == sample_task.title

    def test_update_task_completed(self, session: Session, sample_task):
        """Test updating task completed status."""
        repository = TaskRepository(session)
        update_data = TaskUpdate(completed=True)

        updated_task = repository.update(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.completed is True

    def test_update_task_all_fields(self, session: Session, sample_task):
        """Test updating all fields at once."""
        repository = TaskRepository(session)
        update_data = TaskUpdate(
            title="All New",
            description="Completely Updated",
            completed=True
        )

        updated_task = repository.update(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.title == "All New"
        assert updated_task.description == "Completely Updated"
        assert updated_task.completed is True

    def test_update_task_partial_fields(self, session: Session, sample_task):
        """Test updating only some fields (partial update)."""
        repository = TaskRepository(session)
        original_title = sample_task.title
        update_data = TaskUpdate(completed=True)

        updated_task = repository.update(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.completed is True
        assert updated_task.title == original_title  # Should remain unchanged

    def test_update_task_nonexistent(self, session: Session):
        """Test updating a non-existent task."""
        repository = TaskRepository(session)
        update_data = TaskUpdate(title="Should Fail")

        updated_task = repository.update(999, update_data)

        assert updated_task is None

    def test_update_task_updates_timestamp(self, session: Session, sample_task):
        """Test that updated_at timestamp is updated."""
        repository = TaskRepository(session)
        original_updated_at = sample_task.updated_at

        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)

        update_data = TaskUpdate(title="New Title")
        updated_task = repository.update(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.updated_at > original_updated_at

    def test_update_task_persisted_in_db(self, session: Session, sample_task):
        """Test that updates are persisted in the database."""
        repository = TaskRepository(session)
        update_data = TaskUpdate(title="Persisted Update")

        repository.update(sample_task.id, update_data)

        # Query directly from database to verify
        statement = select(Task).where(Task.id == sample_task.id)
        db_task = session.exec(statement).first()

        assert db_task is not None
        assert db_task.title == "Persisted Update"

    def test_update_task_to_none(self, session: Session, sample_task):
        """Test setting optional field to None."""
        repository = TaskRepository(session)
        update_data = TaskUpdate(description=None)

        updated_task = repository.update(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.description is None


class TestTaskRepositoryDelete:
    """Tests for TaskRepository.delete method."""

    def test_delete_existing_task(self, session: Session, sample_task):
        """Test deleting an existing task."""
        repository = TaskRepository(session)

        result = repository.delete(sample_task.id)

        assert result is True

        # Verify task is deleted
        deleted_task = repository.get_by_id(sample_task.id)
        assert deleted_task is None

    def test_delete_nonexistent_task(self, session: Session):
        """Test deleting a non-existent task."""
        repository = TaskRepository(session)

        result = repository.delete(999)

        assert result is False

    def test_delete_negative_id(self, session: Session):
        """Test deleting with negative ID."""
        repository = TaskRepository(session)

        result = repository.delete(-1)

        assert result is False

    def test_delete_task_removed_from_db(self, session: Session, sample_task):
        """Test that deleted task is removed from database."""
        repository = TaskRepository(session)

        repository.delete(sample_task.id)

        # Query directly from database to verify
        statement = select(Task).where(Task.id == sample_task.id)
        db_task = session.exec(statement).first()

        assert db_task is None

    def test_delete_one_task_leaves_others(self, session: Session, multiple_tasks):
        """Test that deleting one task doesn't affect others."""
        repository = TaskRepository(session)

        # Delete the first task
        deleted_id = multiple_tasks[0].id
        repository.delete(deleted_id)

        # Verify other tasks still exist
        remaining_tasks = repository.get_all()
        assert len(remaining_tasks) == 2

        remaining_ids = [task.id for task in remaining_tasks]
        assert deleted_id not in remaining_ids

    def test_delete_all_tasks_one_by_one(self, session: Session, multiple_tasks):
        """Test deleting all tasks one by one."""
        repository = TaskRepository(session)

        for task in multiple_tasks:
            result = repository.delete(task.id)
            assert result is True

        # Verify all tasks are deleted
        remaining_tasks = repository.get_all()
        assert len(remaining_tasks) == 0


class TestTaskRepositoryEdgeCases:
    """Edge case tests for TaskRepository."""

    def test_concurrent_creates(self, session: Session):
        """Test creating multiple tasks rapidly."""
        repository = TaskRepository(session)

        tasks = []
        for i in range(10):
            task = repository.create(TaskCreate(title=f"Task {i}"))
            tasks.append(task)

        assert len(tasks) == 10
        # Verify all have unique IDs
        ids = [task.id for task in tasks]
        assert len(ids) == len(set(ids))

    def test_update_after_delete_fails(self, session: Session, sample_task):
        """Test that updating a deleted task fails."""
        repository = TaskRepository(session)

        # Delete the task
        repository.delete(sample_task.id)

        # Try to update the deleted task
        update_data = TaskUpdate(title="Should Fail")
        result = repository.update(sample_task.id, update_data)

        assert result is None

    def test_get_after_delete_returns_none(self, session: Session, sample_task):
        """Test that getting a deleted task returns None."""
        repository = TaskRepository(session)

        # Delete the task
        repository.delete(sample_task.id)

        # Try to get the deleted task
        result = repository.get_by_id(sample_task.id)

        assert result is None

    def test_double_delete_returns_false(self, session: Session, sample_task):
        """Test that deleting an already deleted task returns False."""
        repository = TaskRepository(session)

        # First delete
        first_result = repository.delete(sample_task.id)
        assert first_result is True

        # Second delete
        second_result = repository.delete(sample_task.id)
        assert second_result is False

    def test_empty_update_preserves_data(self, session: Session, sample_task):
        """Test that update with no fields preserves original data."""
        repository = TaskRepository(session)

        original_title = sample_task.title
        original_description = sample_task.description
        original_completed = sample_task.completed

        # Update with empty data
        update_data = TaskUpdate()
        updated_task = repository.update(sample_task.id, update_data)

        assert updated_task is not None
        assert updated_task.title == original_title
        assert updated_task.description == original_description
        assert updated_task.completed == original_completed
