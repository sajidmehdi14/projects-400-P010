---
name: pytest-tdd-generator
description: Generate comprehensive pytest test cases for FastAPI routes with positive, negative, and edge cases. Use when user requests test generation for API endpoints, asks to create TDD tests, references specific routes or route files, or describes features/workflows that need testing. Triggers include phrases like 'generate tests for', 'create pytest tests', 'test my API endpoint', 'TDD for [feature]', or when pointing to route files.
---

# Pytest TDD Generator

Generate comprehensive pytest test cases for FastAPI routes following TDD best practices. Creates positive, negative, and edge case tests with proper fixtures and structure.

## Quick Start

When user requests test generation:

1. **Understand the endpoint** - Get route details (path, method, parameters, auth requirements)
2. **Read route file if provided** - Use Read tool to examine actual implementation
3. **Identify test categories** - Determine positive, negative, and edge cases
4. **Generate test code** - Create structured pytest tests with fixtures
5. **Provide usage instructions** - Include setup and execution commands

## Test Generation Workflow

### Step 1: Gather Endpoint Information

Extract or confirm:
- HTTP method (GET, POST, PUT, PATCH, DELETE)
- Route path (e.g., `/users/{user_id}`)
- Request body schema (for POST/PUT/PATCH)
- Query parameters (for GET)
- Path parameters
- Authentication requirements
- Expected responses (status codes, response schemas)

**If user provides a file path**, read it first to understand the implementation:

```python
# Example: Reading a routes file
# Use Read tool on the file, then analyze the route definitions
```

### Step 2: Determine Test Categories

For each endpoint, identify:

**Positive Cases** (Expected Success):
- Valid input returns expected response
- Correct status codes (200, 201, 204)
- Response matches schema
- Successful database operations

**Negative Cases** (Error Handling):
- Missing required fields (422)
- Invalid data types/formats (422)
- Authentication failures (401)
- Authorization failures (403)
- Resource not found (404)
- Duplicate resources (409)
- Business logic violations

**Edge Cases** (Boundary Conditions):
- Empty strings, zero values, null
- Maximum length inputs
- Special characters, unicode
- Invalid ID formats
- Pagination boundaries
- Already deleted resources

Refer to [fastapi_testing_guide.md](references/fastapi_testing_guide.md) for detailed patterns.

### Step 3: Generate Test Structure

Create organized test file with:

1. **Imports** - TestClient, pytest, fixtures
2. **Test class** - Group related endpoint tests
3. **Descriptive test names** - Format: `test_<action>_<scenario>`
4. **Clear docstrings** - Indicate test category (Positive/Negative/Edge)
5. **AAA pattern** - Arrange, Act, Assert
6. **Proper assertions** - Verify status codes, response structure, error messages

### Step 4: Include Fixtures Setup

Provide `conftest.py` template with:
- Test client fixture
- Database session fixtures
- Authentication fixtures
- Sample data fixtures

Use [conftest_template.py](assets/conftest_template.py) as starting point.

### Step 5: Structure Output

Return the following in order:

1. **Overview** - Brief description of what's being tested
2. **Test file code** - Complete pytest test file
3. **Fixtures** (if needed) - conftest.py content or additional fixtures
4. **Setup instructions** - How to install dependencies and configure
5. **Usage example** - Commands to run the tests

## Generation Guidelines

### Test Naming Convention

Use clear, descriptive names:
- `test_create_user_success` - Positive case
- `test_create_user_missing_field` - Negative case
- `test_create_user_empty_string` - Edge case
- `test_get_user_not_found` - Negative case
- `test_delete_user_already_deleted` - Edge case

### Code Structure

```python
class TestUserEndpoints:
    """Tests for user-related endpoints"""

    def test_create_user_success(self, client):
        """Positive: Successfully create a new user"""
        # Arrange
        payload = {"email": "test@example.com", "name": "Test User"}

        # Act
        response = client.post("/users", json=payload)

        # Assert
        assert response.status_code == 201
        assert response.json()["email"] == payload["email"]

    def test_create_user_missing_email(self, client):
        """Negative: Missing required email field"""
        payload = {"name": "Test User"}
        response = client.post("/users", json=payload)

        assert response.status_code == 422
        assert "detail" in response.json()
```

### Use Parametrize for Similar Cases

When testing multiple similar inputs:

```python
@pytest.mark.parametrize("invalid_email", [
    "notanemail",
    "@example.com",
    "user@",
    "",
])
def test_create_user_invalid_emails(client, invalid_email):
    """Edge: Various invalid email formats"""
    payload = {"email": invalid_email, "name": "Test"}
    response = client.post("/users", json=payload)
    assert response.status_code == 422
```

### Complete Response Validation

Always validate:
- Status code
- Response structure (keys present)
- Specific field values when relevant
- Error messages (for negative cases)
- Headers when relevant (Location for 201, etc.)

## Common Endpoint Patterns

### POST Endpoint Tests (Create)

Minimum coverage:
1. ✅ Positive: Successful creation with valid data
2. ❌ Negative: Missing required fields
3. ❌ Negative: Invalid data types
4. ❌ Negative: Duplicate resource (if applicable)
5. 🔧 Edge: Empty strings for text fields
6. 🔧 Edge: Maximum length inputs
7. 🔧 Edge: Special characters

### GET Endpoint Tests (Read Single)

Minimum coverage:
1. ✅ Positive: Successfully retrieve existing resource
2. ❌ Negative: Resource not found (404)
3. 🔧 Edge: Invalid ID format
4. 🔧 Edge: Negative or zero ID

### GET Endpoint Tests (List)

Minimum coverage:
1. ✅ Positive: List with pagination
2. ✅ Positive: List with filters
3. 🔧 Edge: Empty results
4. 🔧 Edge: Invalid pagination parameters
5. 🔧 Edge: First page, last page boundaries

### PUT/PATCH Endpoint Tests (Update)

Minimum coverage:
1. ✅ Positive: Successful update
2. ❌ Negative: Resource not found
3. ❌ Negative: Unauthorized (if protected)
4. ❌ Negative: Invalid data
5. 🔧 Edge: Partial update (PATCH only)
6. 🔧 Edge: Update with same values

### DELETE Endpoint Tests

Minimum coverage:
1. ✅ Positive: Successful deletion
2. ❌ Negative: Resource not found
3. ❌ Negative: Unauthorized (if protected)
4. 🔧 Edge: Delete already deleted resource

### Protected Endpoints (Auth Required)

Additional coverage:
1. ❌ Negative: No authentication token (401)
2. ❌ Negative: Invalid token (401)
3. ❌ Negative: Insufficient permissions (403)
4. ✅ Positive: Valid token with proper permissions

## Example Output Format

When generating tests, provide output in this structure:

### 1. Skill Description
Brief overview of the generated tests.

### 2. Inputs
List what endpoint information was used (path, method, auth, etc.).

### 3. Outputs
Describe what test file(s) were created.

### 4. CLI Usage Example

```bash
# Install dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_users.py

# Run with coverage
pytest --cov=app tests/

# Run only specific test class
pytest tests/test_users.py::TestUserEndpoints

# Run with verbose output
pytest -v tests/
```

### 5. Pytest Code

Provide complete, ready-to-use test code including:
- Test file with all test cases
- conftest.py if custom fixtures needed
- Any additional setup files

## Resources

### Testing Guide
See [fastapi_testing_guide.md](references/fastapi_testing_guide.md) for:
- Detailed testing patterns for each HTTP method
- FastAPI-specific fixtures and setup
- Authentication testing patterns
- Database mocking strategies
- Response validation best practices

### Templates
Use these as starting points:
- [conftest_template.py](assets/conftest_template.py) - Standard test fixtures
- [test_example.py](assets/test_example.py) - Comprehensive example tests

## Best Practices

1. **Test isolation** - Each test should be independent
2. **Use fixtures** - Avoid setup duplication
3. **Clear assertions** - One concept per test
4. **Descriptive names** - Test name explains what's tested
5. **Mock external dependencies** - Database, APIs, file systems
6. **Validate error messages** - Ensure meaningful error responses
7. **Cover happy path first** - Then negative and edge cases
8. **Use parametrize** - For testing multiple similar inputs
9. **Test response structure** - Not just status codes
10. **Document edge cases** - Explain why edge case is tested
