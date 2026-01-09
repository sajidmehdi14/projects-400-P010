"""
Pytest configuration and fixtures for FastAPI testing.

This template provides common fixtures for FastAPI applications.
Customize based on your application's needs.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import your FastAPI app
# from app.main import app
# from app.database import Base, get_db
# from app.models import User  # Import your models


# --- Test Database Setup ---

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Base.metadata.create_all(bind=engine)
    yield engine
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Provide a transactional database session for testing"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with overridden database dependency"""

    # Override the database dependency
    # def override_get_db():
    #     try:
    #         yield db_session
    #     finally:
    #         pass

    # app.dependency_overrides[get_db] = override_get_db

    # with TestClient(app) as test_client:
    #     yield test_client

    # app.dependency_overrides.clear()

    # For now, return a basic client (uncomment above when app is available)
    # from app.main import app
    # yield TestClient(app)
    pass


# --- Authentication Fixtures ---

@pytest.fixture
def test_user(db_session):
    """Create a test user in the database"""
    # user = User(
    #     email="testuser@example.com",
    #     username="testuser",
    #     hashed_password="hashed_password_here"
    # )
    # db_session.add(user)
    # db_session.commit()
    # db_session.refresh(user)
    # return user
    pass


@pytest.fixture
def auth_token(test_user):
    """Generate a valid authentication token for test user"""
    # from app.auth import create_access_token
    # return create_access_token(data={"sub": test_user.email})
    pass


@pytest.fixture
def auth_headers(auth_token):
    """Provide authentication headers with valid token"""
    # return {"Authorization": f"Bearer {auth_token}"}
    pass


# --- Data Fixtures ---

@pytest.fixture
def sample_item_data():
    """Provide sample item data for testing"""
    return {
        "name": "Test Item",
        "description": "A test item description",
        "price": 29.99,
        "in_stock": True
    }


@pytest.fixture
def multiple_test_items(db_session):
    """Create multiple test items in database"""
    # items = [
    #     Item(name=f"Item {i}", price=i * 10.0)
    #     for i in range(1, 6)
    # ]
    # for item in items:
    #     db_session.add(item)
    # db_session.commit()
    # for item in items:
    #     db_session.refresh(item)
    # return items
    pass


# --- Mock Fixtures ---

@pytest.fixture
def mock_external_api(monkeypatch):
    """Mock external API calls"""
    def mock_api_call(*args, **kwargs):
        return {"status": "success", "data": {}}

    # monkeypatch.setattr("app.services.external_api_call", mock_api_call)
    return mock_api_call


# --- Pytest Configuration ---

def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
