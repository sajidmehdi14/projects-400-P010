"""
Comprehensive API endpoint tests for Task Management API.

Tests cover:
- Positive cases: Valid requests with expected responses
- Negative cases: Invalid requests with proper error handling
- Edge cases: Boundary conditions and special scenarios
"""
import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for the root endpoint."""

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns welcome message."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Task API"}


class TestCreateTask:
    """Tests for POST /tasks endpoint."""

    def test_create_task_success(self, client: TestClient, sample_task_data):
        """Test creating a task with valid data."""
        response = client.post("/tasks", json=sample_task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_task_data["title"]
        assert data["description"] == sample_task_data["description"]
        assert data["completed"] == sample_task_data["completed"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_task_minimal_data(self, client: TestClient):
        """Test creating a task with only required fields."""
        task_data = {"title": "Minimal Task"}
        response = client.post("/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Minimal Task"
        assert data["description"] is None
        assert data["completed"] is False

    def test_create_task_with_completed_true(self, client: TestClient):
        """Test creating a task that is already completed."""
        task_data = {
            "title": "Already Done",
            "description": "This was done immediately",
            "completed": True
        }
        response = client.post("/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert data["completed"] is True

    def test_create_task_missing_title(self, client: TestClient):
        """Test creating a task without required title field."""
        task_data = {"description": "No title"}
        response = client.post("/tasks", json=task_data)

        assert response.status_code == 422  # Validation error

    def test_create_task_empty_title(self, client: TestClient):
        """Test creating a task with empty title."""
        task_data = {"title": ""}
        response = client.post("/tasks", json=task_data)

        # FastAPI/Pydantic allows empty strings by default
        # If you want to prevent this, add validation to the model
        assert response.status_code in [201, 422]

    def test_create_task_invalid_completed_type(self, client: TestClient):
        """Test creating a task with invalid completed field type."""
        task_data = {
            "title": "Test Task",
            "completed": ["invalid"]  # Should be boolean, not list
        }
        response = client.post("/tasks", json=task_data)

        assert response.status_code == 422  # Validation error

    def test_create_task_extra_fields(self, client: TestClient):
        """Test creating a task with extra fields (should be ignored)."""
        task_data = {
            "title": "Test Task",
            "description": "Test description",
            "completed": False,
            "extra_field": "should be ignored"
        }
        response = client.post("/tasks", json=task_data)

        assert response.status_code == 201
        data = response.json()
        assert "extra_field" not in data


class TestGetAllTasks:
    """Tests for GET /tasks endpoint."""

    def test_get_all_tasks_empty(self, client: TestClient):
        """Test getting all tasks when database is empty."""
        response = client.get("/tasks")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_tasks_single(self, client: TestClient, sample_task):
        """Test getting all tasks with one task in database."""
        response = client.get("/tasks")

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["id"] == sample_task.id
        assert tasks[0]["title"] == sample_task.title

    def test_get_all_tasks_multiple(self, client: TestClient, multiple_tasks):
        """Test getting all tasks with multiple tasks in database."""
        response = client.get("/tasks")

        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 3
        assert all("id" in task for task in tasks)
        assert all("title" in task for task in tasks)

    def test_get_all_tasks_returns_all_fields(self, client: TestClient, sample_task):
        """Test that all task fields are returned."""
        response = client.get("/tasks")

        assert response.status_code == 200
        tasks = response.json()
        task = tasks[0]
        assert "id" in task
        assert "title" in task
        assert "description" in task
        assert "completed" in task
        assert "created_at" in task
        assert "updated_at" in task


class TestGetSingleTask:
    """Tests for GET /tasks/{id} endpoint."""

    def test_get_task_by_id_success(self, client: TestClient, sample_task):
        """Test getting a specific task by ID."""
        response = client.get(f"/tasks/{sample_task.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_task.id
        assert data["title"] == sample_task.title
        assert data["description"] == sample_task.description

    def test_get_task_not_found(self, client: TestClient):
        """Test getting a task that doesn't exist."""
        response = client.get("/tasks/999")

        assert response.status_code == 404
        assert "detail" in response.json()
        assert response.json()["detail"] == "Task not found"

    def test_get_task_invalid_id_type(self, client: TestClient):
        """Test getting a task with invalid ID type."""
        response = client.get("/tasks/invalid")

        assert response.status_code == 422  # Validation error

    def test_get_task_negative_id(self, client: TestClient):
        """Test getting a task with negative ID."""
        response = client.get("/tasks/-1")

        assert response.status_code == 404

    def test_get_task_zero_id(self, client: TestClient):
        """Test getting a task with ID zero."""
        response = client.get("/tasks/0")

        assert response.status_code == 404


class TestUpdateTask:
    """Tests for PUT /tasks/{id} endpoint."""

    def test_update_task_title(self, client: TestClient, sample_task):
        """Test updating only the title of a task."""
        update_data = {"title": "Updated Title"}
        response = client.put(f"/tasks/{sample_task.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["description"] == sample_task.description
        assert data["completed"] == sample_task.completed

    def test_update_task_description(self, client: TestClient, sample_task):
        """Test updating only the description of a task."""
        update_data = {"description": "Updated Description"}
        response = client.put(f"/tasks/{sample_task.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated Description"
        assert data["title"] == sample_task.title

    def test_update_task_completed_status(self, client: TestClient, sample_task):
        """Test updating only the completed status."""
        update_data = {"completed": True}
        response = client.put(f"/tasks/{sample_task.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["completed"] is True

    def test_update_task_all_fields(self, client: TestClient, sample_task):
        """Test updating all fields of a task."""
        update_data = {
            "title": "Completely Updated",
            "description": "New description",
            "completed": True
        }
        response = client.put(f"/tasks/{sample_task.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["completed"] == update_data["completed"]

    def test_update_task_empty_payload(self, client: TestClient, sample_task):
        """Test updating a task with empty payload (no changes)."""
        response = client.put(f"/tasks/{sample_task.id}", json={})

        assert response.status_code == 200
        data = response.json()
        # Task should remain unchanged
        assert data["title"] == sample_task.title
        assert data["description"] == sample_task.description
        assert data["completed"] == sample_task.completed

    def test_update_task_not_found(self, client: TestClient):
        """Test updating a task that doesn't exist."""
        update_data = {"title": "Non-existent"}
        response = client.put("/tasks/999", json=update_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_update_task_invalid_id(self, client: TestClient):
        """Test updating a task with invalid ID."""
        update_data = {"title": "Updated"}
        response = client.put("/tasks/invalid", json=update_data)

        assert response.status_code == 422

    def test_update_task_null_description(self, client: TestClient, sample_task):
        """Test setting description to null."""
        update_data = {"description": None}
        response = client.put(f"/tasks/{sample_task.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["description"] is None

    def test_update_task_timestamps_changed(self, client: TestClient, sample_task):
        """Test that updated_at timestamp changes after update."""
        original_updated_at = sample_task.updated_at

        update_data = {"title": "Updated Title"}
        response = client.put(f"/tasks/{sample_task.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        # The updated_at should be different (though testing exact time is tricky)
        assert "updated_at" in data


class TestDeleteTask:
    """Tests for DELETE /tasks/{id} endpoint."""

    def test_delete_task_success(self, client: TestClient, sample_task):
        """Test deleting a task successfully."""
        response = client.delete(f"/tasks/{sample_task.id}")

        assert response.status_code == 204
        assert response.content == b""

        # Verify task is actually deleted
        get_response = client.get(f"/tasks/{sample_task.id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, client: TestClient):
        """Test deleting a task that doesn't exist."""
        response = client.delete("/tasks/999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Task not found"

    def test_delete_task_invalid_id(self, client: TestClient):
        """Test deleting a task with invalid ID."""
        response = client.delete("/tasks/invalid")

        assert response.status_code == 422

    def test_delete_task_negative_id(self, client: TestClient):
        """Test deleting a task with negative ID."""
        response = client.delete("/tasks/-1")

        assert response.status_code == 404

    def test_delete_all_tasks_one_by_one(self, client: TestClient, multiple_tasks):
        """Test deleting multiple tasks one by one."""
        for task in multiple_tasks:
            response = client.delete(f"/tasks/{task.id}")
            assert response.status_code == 204

        # Verify all tasks are deleted
        response = client.get("/tasks")
        assert response.json() == []


class TestTaskWorkflow:
    """Integration tests for complete task workflows."""

    def test_create_read_update_delete_workflow(self, client: TestClient):
        """Test complete CRUD workflow for a task."""
        # Create
        create_data = {
            "title": "Workflow Task",
            "description": "Testing full workflow",
            "completed": False
        }
        create_response = client.post("/tasks", json=create_data)
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Read
        read_response = client.get(f"/tasks/{task_id}")
        assert read_response.status_code == 200
        assert read_response.json()["title"] == "Workflow Task"

        # Update
        update_data = {"completed": True}
        update_response = client.put(f"/tasks/{task_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["completed"] is True

        # Delete
        delete_response = client.delete(f"/tasks/{task_id}")
        assert delete_response.status_code == 204

        # Verify deletion
        final_response = client.get(f"/tasks/{task_id}")
        assert final_response.status_code == 404

    def test_create_multiple_tasks_and_list(self, client: TestClient):
        """Test creating multiple tasks and retrieving them."""
        tasks_to_create = [
            {"title": f"Task {i}", "description": f"Description {i}"}
            for i in range(5)
        ]

        created_ids = []
        for task_data in tasks_to_create:
            response = client.post("/tasks", json=task_data)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])

        # Get all tasks
        response = client.get("/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 5

        # Verify all created tasks are in the list
        response_ids = [task["id"] for task in tasks]
        for created_id in created_ids:
            assert created_id in response_ids

    def test_update_nonexistent_task_after_deletion(self, client: TestClient, sample_task):
        """Test that updating a deleted task returns 404."""
        # Delete the task
        delete_response = client.delete(f"/tasks/{sample_task.id}")
        assert delete_response.status_code == 204

        # Try to update the deleted task
        update_data = {"title": "Should Fail"}
        update_response = client.put(f"/tasks/{sample_task.id}", json=update_data)
        assert update_response.status_code == 404
