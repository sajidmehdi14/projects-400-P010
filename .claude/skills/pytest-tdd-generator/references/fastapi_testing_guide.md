# FastAPI Testing Guide

## Test Client Setup

FastAPI uses Starlette's TestClient for testing:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
```

## Test Case Categories

### Positive Cases
Tests that verify expected behavior with valid inputs:
- Valid request data returns expected response
- Correct status codes (200, 201, etc.)
- Response schema matches specification
- Successful database operations
- Proper data transformations

### Negative Cases
Tests that verify proper error handling:
- Invalid request data returns appropriate error
- Missing required fields (422 Unprocessable Entity)
- Invalid data types or formats
- Authentication/authorization failures (401, 403)
- Resource not found (404)
- Duplicate resource creation (409 Conflict)
- Business logic validation failures

### Edge Cases
Tests for boundary conditions and unusual inputs:
- Empty strings, zero values, null values
- Maximum length strings
- Very large numbers
- Special characters and unicode
- Concurrent requests
- Pagination boundaries (first page, last page, empty results)
- Rate limiting edge cases
- Timezone and datetime edge cases

## Common Testing Patterns

### Testing GET Endpoints

```python
def test_get_item_success(client):
    """Positive: Successfully retrieve an item"""
    response = client.get("/items/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_get_item_not_found(client):
    """Negative: Item does not exist"""
    response = client.get("/items/99999")
    assert response.status_code == 404

def test_get_item_invalid_id(client):
    """Edge: Invalid ID format"""
    response = client.get("/items/invalid")
    assert response.status_code == 422
```

### Testing POST Endpoints

```python
def test_create_item_success(client):
    """Positive: Successfully create an item"""
    payload = {"name": "Test Item", "price": 10.99}
    response = client.post("/items", json=payload)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Item"

def test_create_item_missing_required_field(client):
    """Negative: Missing required field"""
    payload = {"name": "Test Item"}  # missing price
    response = client.post("/items", json=payload)
    assert response.status_code == 422

def test_create_item_empty_string(client):
    """Edge: Empty string for required field"""
    payload = {"name": "", "price": 10.99}
    response = client.post("/items", json=payload)
    assert response.status_code == 422
```

### Testing PUT/PATCH Endpoints

```python
def test_update_item_success(client):
    """Positive: Successfully update an item"""
    payload = {"name": "Updated Item"}
    response = client.put("/items/1", json=payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Item"

def test_update_item_not_found(client):
    """Negative: Update non-existent item"""
    payload = {"name": "Updated Item"}
    response = client.put("/items/99999", json=payload)
    assert response.status_code == 404
```

### Testing DELETE Endpoints

```python
def test_delete_item_success(client):
    """Positive: Successfully delete an item"""
    response = client.delete("/items/1")
    assert response.status_code == 204

def test_delete_item_not_found(client):
    """Negative: Delete non-existent item"""
    response = client.delete("/items/99999")
    assert response.status_code == 404

def test_delete_item_already_deleted(client):
    """Edge: Delete already deleted item"""
    client.delete("/items/1")
    response = client.delete("/items/1")
    assert response.status_code == 404
```

### Testing Authentication

```python
def test_protected_endpoint_without_auth(client):
    """Negative: Access protected endpoint without token"""
    response = client.get("/protected")
    assert response.status_code == 401

def test_protected_endpoint_with_invalid_token(client):
    """Negative: Access with invalid token"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 401

def test_protected_endpoint_with_valid_token(client):
    """Positive: Access with valid token"""
    token = "valid_token"  # or generate from fixture
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/protected", headers=headers)
    assert response.status_code == 200
```

### Testing Query Parameters

```python
def test_list_items_with_pagination(client):
    """Positive: Pagination works correctly"""
    response = client.get("/items?skip=0&limit=10")
    assert response.status_code == 200
    assert len(response.json()) <= 10

def test_list_items_with_filters(client):
    """Positive: Filtering works correctly"""
    response = client.get("/items?category=electronics")
    assert response.status_code == 200
    for item in response.json():
        assert item["category"] == "electronics"

def test_list_items_invalid_pagination(client):
    """Edge: Invalid pagination parameters"""
    response = client.get("/items?skip=-1&limit=0")
    assert response.status_code == 422
```

## Fixtures and Setup

### Database Fixtures

```python
@pytest.fixture
def db_session():
    """Provide a transactional database session"""
    # Setup: create session
    session = SessionLocal()
    yield session
    # Teardown: rollback and close
    session.rollback()
    session.close()

@pytest.fixture
def test_user(db_session):
    """Create a test user in database"""
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
```

### Authentication Fixtures

```python
@pytest.fixture
def auth_token(test_user):
    """Generate authentication token for test user"""
    return create_access_token(data={"sub": test_user.email})

@pytest.fixture
def auth_headers(auth_token):
    """Provide authentication headers"""
    return {"Authorization": f"Bearer {auth_token}"}
```

## Testing Best Practices

1. **Use descriptive test names** - Test name should describe what is being tested
2. **Follow AAA pattern** - Arrange, Act, Assert
3. **One assertion per concept** - Don't mix multiple concepts in one test
4. **Use fixtures for setup** - Avoid duplication with pytest fixtures
5. **Test isolation** - Each test should be independent
6. **Mock external dependencies** - Database, APIs, file systems
7. **Test error messages** - Verify error responses contain useful information
8. **Use parametrize for similar cases** - Reduce code duplication

```python
@pytest.mark.parametrize("invalid_email", [
    "notanemail",
    "@example.com",
    "user@",
    "user@.com",
    ""
])
def test_register_invalid_email(client, invalid_email):
    """Edge: Various invalid email formats"""
    payload = {"email": invalid_email, "password": "pass123"}
    response = client.post("/register", json=payload)
    assert response.status_code == 422
```

## Response Validation

Always validate:
- Status code
- Response schema structure
- Specific field values when relevant
- Error messages and error codes
- Headers when relevant (Location for 201, etc.)

```python
def test_create_user_response_structure(client):
    """Positive: Response has correct structure"""
    payload = {"email": "new@example.com", "name": "New User"}
    response = client.post("/users", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert data["email"] == payload["email"]
    assert "created_at" in data
```
