"""
Pytest configuration and fixtures for Task API tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_session
from app.models import Task


@pytest.fixture(name="session")
def session_fixture():
    """
    Create a fresh in-memory database session for each test.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Create a test client with database session dependency override.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="sample_task_data")
def sample_task_data_fixture():
    """
    Sample task data for testing.
    """
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "completed": False
    }


@pytest.fixture(name="sample_task")
def sample_task_fixture(session: Session, sample_task_data):
    """
    Create a sample task in the database for testing.
    """
    task = Task(**sample_task_data)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture(name="multiple_tasks")
def multiple_tasks_fixture(session: Session):
    """
    Create multiple tasks in the database for testing.
    """
    tasks_data = [
        {"title": "Task 1", "description": "First task", "completed": False},
        {"title": "Task 2", "description": "Second task", "completed": True},
        {"title": "Task 3", "description": "Third task", "completed": False},
    ]

    tasks = []
    for task_data in tasks_data:
        task = Task(**task_data)
        session.add(task)
        tasks.append(task)

    session.commit()
    for task in tasks:
        session.refresh(task)

    return tasks
