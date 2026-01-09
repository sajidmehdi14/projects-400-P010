"""
Example test file demonstrating comprehensive pytest test patterns for FastAPI.

This shows the structure and organization of tests with positive, negative, and edge cases.
"""

import pytest
from fastapi.testclient import TestClient


class TestUserEndpoints:
    """Tests for user-related endpoints"""

    # --- POST /users (Create User) ---

    def test_create_user_success(self, client):
        """Positive: Successfully create a new user with valid data"""
        payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "SecurePass123!"
        }
        response = client.post("/users", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        assert "id" in data
        assert "password" not in data  # Password should not be returned
        assert "created_at" in data

    def test_create_user_missing_required_field(self, client):
        """Negative: Attempt to create user without required email field"""
        payload = {
            "username": "newuser",
            "password": "SecurePass123!"
        }
        response = client.post("/users", json=payload)

        assert response.status_code == 422
        assert "detail" in response.json()

    def test_create_user_invalid_email_format(self, client):
        """Negative: Attempt to create user with invalid email format"""
        payload = {
            "email": "not-an-email",
            "username": "newuser",
            "password": "SecurePass123!"
        }
        response = client.post("/users", json=payload)

        assert response.status_code == 422

    def test_create_user_duplicate_email(self, client, test_user):
        """Negative: Attempt to create user with existing email"""
        payload = {
            "email": test_user.email,  # Email already exists
            "username": "differentuser",
            "password": "SecurePass123!"
        }
        response = client.post("/users", json=payload)

        assert response.status_code == 409  # Conflict
        assert "already exists" in response.json()["detail"].lower()

    def test_create_user_weak_password(self, client):
        """Negative: Attempt to create user with weak password"""
        payload = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "123"  # Too short/weak
        }
        response = client.post("/users", json=payload)

        assert response.status_code == 422

    @pytest.mark.parametrize("invalid_email", [
        "",  # Empty string
        "   ",  # Whitespace only
        "@example.com",  # Missing local part
        "user@",  # Missing domain
        "user@.com",  # Invalid domain
    ])
    def test_create_user_invalid_emails(self, client, invalid_email):
        """Edge: Various invalid email formats"""
        payload = {
            "email": invalid_email,
            "username": "newuser",
            "password": "SecurePass123!"
        }
        response = client.post("/users", json=payload)

        assert response.status_code == 422

    def test_create_user_empty_username(self, client):
        """Edge: Empty username string"""
        payload = {
            "email": "newuser@example.com",
            "username": "",
            "password": "SecurePass123!"
        }
        response = client.post("/users", json=payload)

        assert response.status_code == 422

    def test_create_user_max_length_username(self, client):
        """Edge: Username at maximum allowed length"""
        payload = {
            "email": "newuser@example.com",
            "username": "a" * 50,  # Assuming max length is 50
            "password": "SecurePass123!"
        }
        response = client.post("/users", json=payload)

        # Should succeed if within limit
        assert response.status_code in [201, 422]

    # --- GET /users/{user_id} (Get User) ---

    def test_get_user_success(self, client, test_user):
        """Positive: Successfully retrieve user by ID"""
        response = client.get(f"/users/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert "password" not in data

    def test_get_user_not_found(self, client):
        """Negative: Attempt to retrieve non-existent user"""
        response = client.get("/users/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_user_invalid_id_format(self, client):
        """Edge: Invalid user ID format (string instead of int)"""
        response = client.get("/users/invalid-id")

        assert response.status_code == 422

    def test_get_user_negative_id(self, client):
        """Edge: Negative user ID"""
        response = client.get("/users/-1")

        assert response.status_code in [404, 422]

    def test_get_user_zero_id(self, client):
        """Edge: Zero as user ID"""
        response = client.get("/users/0")

        assert response.status_code in [404, 422]

    # --- GET /users (List Users) ---

    def test_list_users_success(self, client, multiple_test_items):
        """Positive: Successfully list users with pagination"""
        response = client.get("/users?skip=0&limit=10")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_list_users_with_filter(self, client):
        """Positive: Filter users by query parameter"""
        response = client.get("/users?username=test")

        assert response.status_code == 200
        data = response.json()
        for user in data:
            assert "test" in user["username"].lower()

    def test_list_users_empty_result(self, client):
        """Edge: Query returns no results"""
        response = client.get("/users?username=nonexistentuser123")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_users_invalid_pagination_negative_skip(self, client):
        """Edge: Negative skip value in pagination"""
        response = client.get("/users?skip=-1&limit=10")

        assert response.status_code == 422

    def test_list_users_invalid_pagination_zero_limit(self, client):
        """Edge: Zero limit value in pagination"""
        response = client.get("/users?skip=0&limit=0")

        assert response.status_code == 422

    def test_list_users_large_limit(self, client):
        """Edge: Very large limit value"""
        response = client.get("/users?skip=0&limit=10000")

        # Should either succeed with max limit or return 422
        assert response.status_code in [200, 422]

    # --- PUT /users/{user_id} (Update User) ---

    def test_update_user_success(self, client, test_user, auth_headers):
        """Positive: Successfully update user information"""
        payload = {"username": "updated_username"}
        response = client.put(
            f"/users/{test_user.id}",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == payload["username"]

    def test_update_user_unauthorized(self, client, test_user):
        """Negative: Attempt to update user without authentication"""
        payload = {"username": "updated_username"}
        response = client.put(f"/users/{test_user.id}", json=payload)

        assert response.status_code == 401

    def test_update_user_forbidden(self, client, test_user, auth_headers):
        """Negative: Attempt to update another user's information"""
        other_user_id = test_user.id + 1
        payload = {"username": "updated_username"}
        response = client.put(
            f"/users/{other_user_id}",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 403

    def test_update_user_not_found(self, client, auth_headers):
        """Negative: Attempt to update non-existent user"""
        payload = {"username": "updated_username"}
        response = client.put(
            "/users/99999",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_update_user_invalid_data(self, client, test_user, auth_headers):
        """Negative: Attempt to update with invalid data"""
        payload = {"email": "not-an-email"}
        response = client.put(
            f"/users/{test_user.id}",
            json=payload,
            headers=auth_headers
        )

        assert response.status_code == 422

    # --- DELETE /users/{user_id} (Delete User) ---

    def test_delete_user_success(self, client, test_user, auth_headers):
        """Positive: Successfully delete user"""
        response = client.delete(
            f"/users/{test_user.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        # Verify user is deleted
        get_response = client.get(f"/users/{test_user.id}")
        assert get_response.status_code == 404

    def test_delete_user_unauthorized(self, client, test_user):
        """Negative: Attempt to delete user without authentication"""
        response = client.delete(f"/users/{test_user.id}")

        assert response.status_code == 401

    def test_delete_user_not_found(self, client, auth_headers):
        """Negative: Attempt to delete non-existent user"""
        response = client.delete("/users/99999", headers=auth_headers)

        assert response.status_code == 404

    def test_delete_user_already_deleted(self, client, test_user, auth_headers):
        """Edge: Attempt to delete already deleted user"""
        # First deletion
        response1 = client.delete(
            f"/users/{test_user.id}",
            headers=auth_headers
        )
        assert response1.status_code == 204

        # Second deletion attempt
        response2 = client.delete(
            f"/users/{test_user.id}",
            headers=auth_headers
        )
        assert response2.status_code == 404
