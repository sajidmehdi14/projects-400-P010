
## Original Project Planning Documentation

# 🔹 Skill 1 — FastAPI CRUD Generator

**Outcome:** Generates full CRUD API from a model
**Measure:** Replaces ~45–60 minutes manual coding

### Claude Code Prompt

```
Create a reusable Claude Code skill using skill-creator skill according to claude code standards.

Name: fastapi_crud_builder

From a SQLModel/Pydantic model, generate:
- FastAPI router
- CRUD endpoints
- Dependency injection
- Status codes

Return:
1. Skill description
2. Inputs
3. Outputs
4. CLI usage example
5. Python code (modular, clean)
```


# 🔹 Skill 2 — pytest TDD Generator

**Outcome:** Creates failing tests first
**Measure:** Improves test coverage + speed

### Claude Code Prompt

```
Create a reusable Claude Code skill using skill-creator skill according to claude code standards.

Name: pytest_tdd_generator

Given API routes, generate pytest test cases:
- Positive cases
- Negative cases
- Edge cases

Return:
1. Skill description
2. Inputs
3. Outputs
4. CLI usage example
5. Pytest code
```
# 🔹 Skill 3 — SQLModel Schema Designer

**Outcome:** Produces production-ready models
**Measure:** Reduces DB design mistakes

### Claude Code Prompt

```
Create a reusable Claude Code skill using skill-creator skill according to claude code standards.

Name: sqlmodel_schema_designer

Given entity description, generate SQLModel classes with:
- Relationships
- Enums
- Timestamps
- Indexes

Return:
1. Skill description
2. Inputs
3. Outputs
4. CLI usage example
5. SQLModel code
```


# 🔹 Skill 4 — FastAPI Code Reviewer

**Outcome:** Finds bugs + architecture flaws
**Measure:** Prevents defects before PR

### Claude Code Prompt

```
Create a reusable Claude Code skill using skill-creator skill according to claude code standards.

Name: fastapi_code_reviewer

Review FastAPI code and return:
- Bugs
- Security issues
- Performance risks
- Design problems

Return:
1. Skill description
2. Inputs
3. Outputs
4. CLI usage example
5. Review format template
```

# 🔹 Skill 5 — API Refactor Architect

**Outcome:** Refactors into clean architecture
**Measure:** Improves maintainability

### Claude Code Prompt

```
Create a reusable Claude Code skill using skill-creator skill according to claude code standards.

Name: api_clean_arch_refactor

Refactor FastAPI app into:
- routers
- services
- models
- repositories

Return:
1. Skill description
2. Inputs
3. Outputs
4. CLI usage example
5. Folder structure + code
```



# Part 2 
#### Prompt 1
Create a FastAPI CRUD API skeleton using SQLModel and dependency injection.
Include folder structure and best practices.
Return only code and folder tree.


#### Prompt 2
Generate pytest test cases for Task CRUD endpoints:
- create task
- list tasks
- update task
- delete task

Tests must fail before implementation.
Return only pytest code.


#### Prompt 3 Tasks APIs
Design SQLModel schemas for a Task Management system.

Include:
- Task table
- Status enum
- Created/updated timestamps

Return SQLModel classes only.


# Part 3
Implement full CRUD Task API using FastAPI + SQLModel.

Routes:
POST /tasks
GET /tasks
GET /tasks/{id}
PUT /tasks/{id}
DELETE /tasks/{id}

Use clean architecture.
Return only code.


#### prompt 2
Refactor API into service layer architecture.

Create:
- routers
- services
- models
- database

Return folder tree + code.


#### Prompt 3
Add global exception handling, validation errors, and proper HTTP status codes to the API.

Return updated FastAPI code only.



#### Prompt 4
Review this FastAPI code like a senior backend architect.

Identify:
- Bugs
- Security risks
- Performance issues
- Design flaws

Return bullet list only.

# Part 3 ( Project Created with claude code & skills)

# Task Management API

A production-ready Task Management API built with FastAPI, SQLModel, and clean architecture principles.

## Project Overview

This project demonstrates building a complete REST API with full CRUD operations (Create, Read, Update, Delete) using modern Python technologies. The implementation follows clean architecture with separation of concerns across routers, services, repositories, and models.

## Tech Stack

| Technology | Purpose |
|-----------|---------|
| FastAPI | Web framework for building APIs |
| SQLModel | SQL database ORM with Pydantic models |
| Uvicorn | ASGI server for running FastAPI |
| pytest | Testing framework with 100+ test cases |
| pytest-cov | Code coverage reporting |
| Python 3.12+ | Programming language |

## Project Structure

```
task-api/
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── routers.py       # API route handlers
│   ├── services.py      # Business logic layer
│   ├── repositories.py  # Data access layer
│   ├── models.py        # SQLModel schemas
│   └── database.py      # Database configuration
├── tests/
│   ├── conftest.py      # Pytest fixtures and configuration
│   ├── test_api.py      # API endpoint tests
│   ├── test_services.py # Service layer tests
│   └── test_repositories.py # Repository layer tests
├── requirements.txt     # Python dependencies
├── pytest.ini          # Pytest configuration
└── README.md           # Documentation
```

## Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation & Setup

### 1. Clone the repository

```bash
cd projects-400-P010
```

### 2. Create a virtual environment

```bash
cd task-api
python -m venv venv
```

### 3. Activate the virtual environment

**Linux/MacOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the API

### Start the development server

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://localhost:8000`

### Access the API documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| POST | `/tasks` | Create a new task |
| GET | `/tasks` | Get all tasks |
| GET | `/tasks/{id}` | Get a specific task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |

## Testing the API

### Using curl

#### 1. Check API is running
```bash
curl http://localhost:8000/
```

Expected response:
```json
{"message": "Task API"}
```

#### 2. Create a new task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive README with setup instructions",
    "completed": false
  }'
```

Expected response:
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive README with setup instructions",
  "completed": false,
  "id": 1,
  "created_at": "2026-01-09T12:00:00.000000",
  "updated_at": "2026-01-09T12:00:00.000000"
}
```

#### 3. Get all tasks
```bash
curl http://localhost:8000/tasks
```

#### 4. Get a specific task
```bash
curl http://localhost:8000/tasks/1
```

#### 5. Update a task
```bash
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

#### 6. Delete a task
```bash
curl -X DELETE http://localhost:8000/tasks/1
```

### Using HTTPie (Alternative)

If you have HTTPie installed:

```bash
# Create task
http POST :8000/tasks title="Test task" description="Testing the API" completed:=false

# Get all tasks
http :8000/tasks

# Update task
http PUT :8000/tasks/1 completed:=true

# Delete task
http DELETE :8000/tasks/1
```

### Using the Interactive Documentation

1. Navigate to http://localhost:8000/docs
2. Click on any endpoint to expand it
3. Click "Try it out"
4. Fill in the parameters
5. Click "Execute"
6. View the response

## Automated Testing with pytest

The project includes a comprehensive test suite using pytest with 100+ test cases covering all layers of the application.

### Test Structure

```
task-api/tests/
├── __init__.py
├── conftest.py          # Shared fixtures and configuration
├── test_api.py          # API endpoint tests (integration)
├── test_services.py     # Service layer tests (unit)
└── test_repositories.py # Repository layer tests (unit)
```

### Test Coverage

The test suite includes:

- **API Tests** (test_api.py): 50+ tests covering all CRUD endpoints
  - Positive cases: Valid requests and expected responses
  - Negative cases: Invalid requests and error handling
  - Edge cases: Boundary conditions and special scenarios
  - Integration workflows: Complete CRUD operations

- **Service Tests** (test_services.py): 30+ tests for business logic
  - Create, read, update, delete operations
  - Data validation and processing
  - Service layer workflows

- **Repository Tests** (test_repositories.py): 40+ tests for data access
  - Database operations
  - Data persistence verification
  - Edge cases and error handling

### Running Tests

#### Install test dependencies

If you haven't already, install the testing dependencies:

```bash
pip install -r requirements.txt
```

This installs:
- `pytest`: Testing framework
- `pytest-cov`: Coverage reporting
- `httpx`: HTTP client for FastAPI testing

#### Run all tests

```bash
pytest
```

#### Run tests with detailed output

```bash
pytest -v
```

#### Run tests with coverage report

```bash
pytest --cov=app --cov-report=term-missing
```

#### Run specific test file

```bash
# API tests only
pytest tests/test_api.py

# Service tests only
pytest tests/test_services.py

# Repository tests only
pytest tests/test_repositories.py
```

#### Run specific test class

```bash
pytest tests/test_api.py::TestCreateTask
```

#### Run specific test function

```bash
pytest tests/test_api.py::TestCreateTask::test_create_task_success
```

#### Run tests in parallel (faster)

Install pytest-xdist first:
```bash
pip install pytest-xdist
pytest -n auto
```

#### Generate HTML coverage report

```bash
pytest --cov=app --cov-report=html
```

Then open `htmlcov/index.html` in your browser.

### Test Output Example

```
================================ test session starts =================================
platform linux -- Python 3.12.0, pytest-7.4.4, pluggy-1.3.0
rootdir: /path/to/task-api
configfile: pytest.ini
plugins: cov-4.1.0
collected 120 items

tests/test_api.py .................................................     [ 42%]
tests/test_services.py ..............................           [ 67%]
tests/test_repositories.py ........................................  [100%]

---------- coverage: platform linux, python 3.12.0 -----------
Name                      Stmts   Miss  Cover   Missing
-------------------------------------------------------
app/__init__.py               0      0   100%
app/database.py              12      0   100%
app/main.py                   8      0   100%
app/models.py                18      0   100%
app/repositories.py          35      0   100%
app/routers.py               30      0   100%
app/services.py              15      0   100%
-------------------------------------------------------
TOTAL                       118      0   100%

================================ 120 passed in 2.45s =================================
```

### Continuous Testing

For development, you can run tests automatically on file changes:

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw
```

### Writing New Tests

When adding new features, follow the existing test structure:

1. **API Tests**: Test HTTP endpoints and responses
   ```python
   def test_new_endpoint(client: TestClient):
       response = client.get("/new-endpoint")
       assert response.status_code == 200
   ```

2. **Service Tests**: Test business logic
   ```python
   def test_new_service_method(session: Session):
       service = TaskService(TaskRepository(session))
       result = service.new_method()
       assert result is not None
   ```

3. **Repository Tests**: Test data access
   ```python
   def test_new_repository_method(session: Session):
       repository = TaskRepository(session)
       result = repository.new_method()
       assert result is not None
   ```

### Test Best Practices

- Each test should be independent and isolated
- Use fixtures for common setup (defined in conftest.py)
- Test one thing per test function
- Use descriptive test names (test_should_do_something_when_condition)
- Cover positive cases, negative cases, and edge cases
- Maintain high test coverage (aim for 90%+)

### Continuous Integration

To run tests in CI/CD pipelines:

```bash
# Run tests with coverage and fail if coverage < 80%
pytest --cov=app --cov-fail-under=80

# Run tests with JUnit XML output for CI tools
pytest --junitxml=test-results.xml
```

## Data Model

### Task

| Field | Type | Description |
|-------|------|-------------|
| id | int | Auto-generated unique identifier |
| title | str | Task title (required) |
| description | str | Task description (optional) |
| completed | bool | Completion status (default: false) |
| created_at | datetime | Auto-generated creation timestamp |
| updated_at | datetime | Auto-generated update timestamp |

## Architecture

The application follows clean architecture principles:

- **Routers**: Handle HTTP requests and responses
- **Services**: Contain business logic
- **Repositories**: Handle data access and persistence
- **Models**: Define data structures and validation
- **Database**: Manage database connections and sessions

## Development Notes

- The API uses SQLite as the default database (stored as `database.db`)
- Database tables are created automatically on startup
- All timestamps are in UTC
- The API follows RESTful conventions

## Troubleshooting

### Port already in use
If port 8000 is already in use, specify a different port:
```bash
uvicorn app.main:app --reload --port 8001
```

### Module not found errors
Ensure the virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Database issues
Delete the `database.db` file and restart the server to recreate the database:
```bash
rm database.db
uvicorn app.main:app --reload
```

## Next Steps

- ✅ Comprehensive pytest test suite (100+ tests with full coverage)
- Implement authentication and authorization
- Add pagination for task listings
- Add filtering and sorting capabilities
- Add search functionality for tasks
- Implement rate limiting
- Add API versioning
- Deploy to production (e.g., using Docker)
- Set up CI/CD pipeline with automated testing
- Add API documentation with more examples

---
