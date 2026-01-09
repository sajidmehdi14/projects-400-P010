# Architecture Patterns

## Direct DB Operations Pattern

**When to use:**
- Small to medium applications
- Rapid prototyping
- Simple CRUD without complex business logic
- When you want minimal abstraction

**Structure:**
- Route handlers directly interact with the database session
- Business logic lives in route handlers
- Fewer files and layers

**Pros:**
- Simple and straightforward
- Easy to understand for beginners
- Less boilerplate code
- Good for getting started quickly

**Cons:**
- Route handlers can become complex
- Harder to test (database coupling)
- Business logic mixed with HTTP handling
- Less reusable across different interfaces

## Repository Pattern

**When to use:**
- Medium to large applications
- Complex business logic
- Multiple interfaces (REST API, GraphQL, CLI)
- When testability is important
- When you want to follow clean architecture

**Structure:**
- Repository class handles all database operations
- Route handlers delegate to repository
- Clear separation of concerns
- Repository injected as dependency

**Pros:**
- Cleaner separation of concerns
- Easier to test (mock repository)
- Business logic reusable
- Route handlers stay thin
- Better for team collaboration

**Cons:**
- More boilerplate
- Additional abstraction layer
- Overkill for simple CRUD

## Session Management Approaches

### Generate Dependency

The generator creates a `get_session()` dependency function:

```python
def get_session():
    """Database session dependency."""
    engine = create_engine("sqlite:///database.db")
    with Session(engine) as session:
        yield session
```

**Use when:**
- Starting a new project
- Want complete control over session lifecycle
- Need to customize session behavior

### Assume Existing Dependency

The generator assumes you have a `get_db()` function:

```python
# Your existing code
def get_db():
    # Your database setup
    yield session

# Generated code uses it
async def create_item(session = Depends(get_db)):
    pass
```

**Use when:**
- Adding to existing project with database setup
- Following your project's conventions
- Integrating with existing dependency injection

## Error Handling

All generated code includes:

### HTTP 404 Not Found
- Raised when item doesn't exist on GET/PUT/DELETE
- Clear error message indicating which resource

### HTTP 409 Conflict
- Unique constraint violations
- Foreign key constraint violations on delete
- Prevents data integrity issues

### HTTP 422 Unprocessable Entity
- Database errors that don't fit other categories
- Fallback for unexpected errors
- Includes error details

### Pydantic Validation
- Automatic validation via Pydantic models
- Type checking and coercion
- FastAPI handles validation errors automatically (HTTP 422)
