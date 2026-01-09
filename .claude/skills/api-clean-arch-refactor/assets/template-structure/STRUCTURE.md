# Clean Architecture Folder Structure

```
app/
├── __init__.py
├── main.py                     # FastAPI app entry point
│
├── core/                       # Core configuration & dependencies
│   ├── __init__.py
│   ├── config.py              # Application settings
│   ├── database.py            # Database connection
│   └── dependencies.py        # Dependency injection
│
├── models/                     # Data models
│   ├── __init__.py
│   ├── user.py                # User models (DB + Pydantic schemas)
│   └── item.py                # Item models (DB + Pydantic schemas)
│
├── repositories/              # Data access layer
│   ├── __init__.py
│   ├── base_repository.py    # Base CRUD operations
│   ├── user_repository.py    # User database operations
│   └── item_repository.py    # Item database operations
│
├── services/                  # Business logic layer
│   ├── __init__.py
│   ├── user_service.py       # User business logic
│   └── item_service.py       # Item business logic
│
└── routers/                   # API endpoints layer
    ├── __init__.py
    ├── users.py              # User endpoints
    └── items.py              # Item endpoints
```

## Layer Responsibilities

**Routers** (Presentation)
- Handle HTTP requests/responses
- Validate input (query params, path params)
- Return appropriate status codes
- NO business logic

**Services** (Business Logic)
- Implement business rules
- Orchestrate operations
- Handle errors & exceptions
- Call repositories for data access

**Repositories** (Data Access)
- Database operations only
- CRUD operations
- Queries and filters
- NO business logic

**Models**
- Database models (SQLAlchemy)
- API schemas (Pydantic)
- Data validation

**Core**
- Configuration
- Database setup
- Dependency injection
