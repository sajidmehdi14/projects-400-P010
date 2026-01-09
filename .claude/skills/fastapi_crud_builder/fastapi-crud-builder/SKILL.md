---
name: fastapi-crud-builder
description: Generate complete FastAPI CRUD routers from SQLModel/Pydantic models with proper dependency injection, status codes, and error handling. Use when users need to create REST API endpoints for database models, want to scaffold CRUD operations, or request FastAPI router generation. Triggers include "generate CRUD", "create FastAPI endpoints", "build REST API for model", or providing a model and asking for API implementation.
---

# FastAPI CRUD Builder

Generate production-ready FastAPI CRUD routers from SQLModel or Pydantic models with proper HTTP status codes, error handling, and dependency injection patterns.

## Quick Start

**Basic generation:**

```bash
python scripts/generate_crud.py "
from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str
" > routers/user.py
```

This generates a complete FastAPI router with:
- POST `/users/` - Create (201)
- GET `/users/` - List with pagination (200)
- GET `/users/{id}` - Get by ID (200/404)
- PUT `/users/{id}` - Update (200/404/409)
- DELETE `/users/{id}` - Delete (204/404/409)

## Usage Workflow

1. **Ask user for architecture preference** (if not specified):
   - Direct DB operations (simpler) or Repository pattern (cleaner separation)
   - Generate session dependency or assume existing `get_db()`

2. **Run the generator script**:
   ```bash
   python scripts/generate_crud.py <model> [options] [-o output_file]
   ```

3. **Review and customize** generated code as needed

4. **Register router** in FastAPI app:
   ```python
   from routers import user
   app.include_router(user.router)
   ```

## Generator Options

### Architecture Pattern

**`--pattern direct`** (default)
- Database operations directly in route handlers
- Simple and straightforward
- Good for small/medium apps or prototyping

**`--pattern repository`**
- Separate repository class for DB operations
- Clean architecture with dependency injection
- Better for larger apps or when testability matters

See [patterns.md](references/patterns.md) for detailed comparison and when to use each.

### Session Management

**`--session generate`** (default)
- Creates `get_session()` dependency in generated code
- Use for new projects or standalone routers
- User must implement their database connection

**`--session assume`**
- Assumes `get_db()` function exists
- Use when adding to existing project with DB setup
- Follows project's existing conventions

### Input Format

The generator accepts:
- **Model code as string** (inline)
- **Path to file** containing the model

### Output

**`-o <file>`** - Write to file
**No `-o`** - Print to stdout

## Generated Code Features

### Automatic Field Handling

- **Primary keys** (`id`) excluded from Create/Update models
- **Timestamps** (`created_at`, `updated_at`) excluded from Create/Update
- **Optional fields** properly typed in request models
- **Type validation** via Pydantic

### Error Handling

All routes include comprehensive error handling:

- **404 Not Found** - Item doesn't exist
- **409 Conflict** - Unique constraint or foreign key violations
- **422 Unprocessable Entity** - Validation or database errors
- **Automatic validation** via Pydantic models

### Status Codes

- `201 Created` - Successful creation
- `200 OK` - Successful read/update
- `204 No Content` - Successful deletion
- `404/409/422` - Error responses

## Examples

### Model from File

```bash
python scripts/generate_crud.py \
    models/product.py \
    --pattern repository \
    --session assume \
    -o routers/product.py
```

### Multiple Models

```bash
for model in models/*.py; do
    basename=$(basename "$model" .py)
    python scripts/generate_crud.py "$model" -o "routers/${basename}.py"
done
```

### Complex Model

```python
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    price: float
    stock: int = 0
    category: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

Generates proper handling for optional fields, defaults, and timestamp exclusion.

## Reference Files

**[patterns.md](references/patterns.md)** - Detailed architecture patterns guide:
- When to use direct vs repository pattern
- Session management approaches
- Error handling strategies

**[examples.md](references/examples.md)** - Complete examples:
- Simple and complex model examples
- Generated code samples
- Integration examples
- CLI usage patterns

## Customization

Generated code is meant to be customized:
- Add custom validation logic
- Extend error handling
- Add authentication/authorization
- Implement filtering/searching
- Add business logic

The generator provides a solid foundation following FastAPI best practices.
