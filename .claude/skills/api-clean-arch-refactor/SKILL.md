---
name: api-clean-arch-refactor
description: Refactor FastAPI applications into clean architecture with routers, services, models, and repositories layers. Use when refactoring monolithic FastAPI code, organizing FastAPI projects, implementing clean architecture, separating concerns in FastAPI apps, or when users request to split their FastAPI application into proper layers. Triggers include requests like "refactor my FastAPI app", "organize into clean architecture", "split into routers and services", "apply clean architecture to FastAPI", or working with main.py files containing mixed route handlers, business logic, and database queries.
---

# FastAPI Clean Architecture Refactoring

Refactor FastAPI applications from monolithic structure into clean architecture with proper separation of concerns across routers, services, models, and repositories.

## When to Use This Skill

Use this skill when:
- User has monolithic FastAPI code (all in main.py or few files)
- Route handlers contain business logic and database queries
- User requests to "refactor", "organize", or "restructure" their FastAPI app
- User wants to implement clean architecture, layered architecture, or separation of concerns
- User mentions wanting routers, services, or repositories

## Quick Assessment

Ask these questions to understand the current structure:
1. Where are your route handlers? (main.py, routes.py, or organized files?)
2. Where are database queries? (in routes, separate file, or dedicated layer?)
3. Do you have Pydantic models and SQLAlchemy models separated?
4. Is business logic in route handlers or separate functions?

Common patterns to refactor:
- **Pattern A**: Everything in main.py (routes + logic + queries)
- **Pattern B**: Routes in separate file, but still contain logic and queries
- **Pattern C**: Some separation exists, but inconsistent or incomplete

## Refactoring Workflow

### Phase 1: Analyze Existing Structure

Read the existing codebase to understand:
- Current file organization
- Where routes are defined
- Where database models are defined
- Where business logic exists
- Database query locations
- Existing dependencies

**Identify the refactoring scope:**
- List all entities/resources (users, items, orders, etc.)
- Map current vs target structure
- Identify shared logic and utilities

### Phase 2: Create Clean Architecture Structure

Create the folder structure following clean architecture principles:

```
app/
├── core/              # Configuration and dependencies
├── models/            # Data models (DB + Pydantic)
├── repositories/      # Data access layer
├── services/          # Business logic layer
└── routers/           # API endpoints layer
```

Reference the template structure in `assets/template-structure/` for complete example.

### Phase 3: Extract Models

**3.1 Extract Database Models**
Move all SQLAlchemy models to `models/` directory:
- One file per entity (e.g., `user.py`, `item.py`)
- Use consistent naming: `EntityDB` for database models
- Include relationships and indexes

**3.2 Create Pydantic Schemas**
For each entity, create API schemas in same file:
- `EntityBase` - shared fields
- `EntityCreate` - for POST requests
- `EntityUpdate` - for PUT/PATCH requests (optional fields)
- `EntityResponse` - for responses (with `model_config`)

**Example:**
```python
# models/user.py
class UserDB(Base):  # Database model
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

class UserCreate(BaseModel):  # API schema
    email: EmailStr
    password: str

class UserResponse(BaseModel):  # API schema
    id: int
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)
```

### Phase 4: Extract Repositories

**4.1 Create Base Repository**
Create `repositories/base_repository.py` with generic CRUD operations using TypeVar for reusability.

**4.2 Create Entity Repositories**
For each entity, create repository extending base:
- Inherits common CRUD (get, get_all, create, update, delete)
- Adds entity-specific queries (get_by_email, search, filter methods)
- Only database operations, NO business logic

**Repository responsibilities:**
- Execute database queries
- Handle joins and filters
- Return database models
- Pagination

**Example:**
```python
# repositories/user_repository.py
class UserRepository(BaseRepository[UserDB]):
    def __init__(self, db: Session):
        super().__init__(UserDB, db)

    def get_by_email(self, email: str) -> Optional[UserDB]:
        return self.db.query(UserDB).filter(UserDB.email == email).first()
```

### Phase 5: Extract Services

**5.1 Identify Business Logic**
Look for logic that should move to services:
- Validation beyond data types (uniqueness, business rules)
- Password hashing, token generation
- Complex calculations or transformations
- Coordinating multiple repository calls
- Error handling with business context

**5.2 Create Service Classes**
For each entity, create service:
- Receives repository via dependency injection
- Implements business logic
- Calls repository methods for data access
- Returns Pydantic schemas (not DB models)
- Raises HTTPException for errors

**Service pattern:**
```python
class EntityService:
    def __init__(self, repository: EntityRepository):
        self.repository = repository

    def create_entity(self, data: EntityCreate) -> EntityResponse:
        # 1. Validate business rules
        # 2. Transform data if needed
        # 3. Create DB model
        # 4. Call repository
        # 5. Return response schema
```

**Example:**
```python
# services/user_service.py
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user_data: UserCreate) -> UserResponse:
        if self.repository.email_exists(user_data.email):
            raise HTTPException(status_code=400, detail="Email exists")

        hashed = pwd_context.hash(user_data.password)
        user = UserDB(email=user_data.email, hashed_password=hashed)

        created_user = self.repository.create(user)
        return UserResponse.model_validate(created_user)
```

### Phase 6: Setup Dependency Injection

**6.1 Create Core Configuration**
Setup `core/config.py`, `core/database.py`, `core/dependencies.py`

**6.2 Define Dependencies**
In `core/dependencies.py`, create dependency chain:
- Database dependency → Repository dependency → Service dependency
- Use `Annotated` with `Depends` for clean injection
- Follow pattern: get_entity_repository → get_entity_service

**Example:**
```python
# core/dependencies.py
DatabaseDep = Annotated[Session, Depends(get_db)]

def get_user_repository(db: DatabaseDep) -> UserRepository:
    return UserRepository(db)

UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]

def get_user_service(repository: UserRepositoryDep) -> UserService:
    return UserService(repository)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
```

### Phase 7: Refactor Routers

**7.1 Create Router Files**
One file per entity in `routers/` directory.

**7.2 Slim Down Route Handlers**
Each endpoint should only:
- Receive request data
- Inject service dependency
- Call service method
- Return response

**No business logic in routes!**

**Before:**
```python
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400)
    hashed = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    return db_user
```

**After:**
```python
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, service: UserServiceDep):
    return service.create_user(user)
```

**7.3 Register Routers**
In `main.py`, include all routers with appropriate prefixes and tags.

### Phase 8: Verification

**8.1 Check Dependencies**
- No circular imports
- Dependency direction: Routers → Services → Repositories
- No database access in routers
- No business logic in repositories

**8.2 Test Endpoints**
- Verify all endpoints work
- Check error handling
- Validate response schemas
- Test edge cases

**8.3 Update Tests**
Update or create tests for each layer:
- Repository tests (with real/test database)
- Service tests (with mocked repositories)
- Router tests (with TestClient)

## Layer Responsibilities

**Routers** (Presentation Layer)
- Handle HTTP requests/responses
- Validate request format (automatically via Pydantic)
- Inject dependencies
- Return appropriate status codes
- NO business logic, NO database access

**Services** (Business Logic Layer)
- Implement business rules and validation
- Orchestrate multiple operations
- Transform between database and API models
- Handle errors with business context
- Call repositories for data access

**Repositories** (Data Access Layer)
- Execute database queries (CRUD + custom)
- Handle filtering, pagination, joins
- Return database models
- NO business logic

**Models**
- Database models (SQLAlchemy) - table structure
- API schemas (Pydantic) - request/response format
- Clear separation and transformation between layers

## Common Scenarios

### Scenario A: Monolithic main.py
**Approach:** Extract in order: Models → Repositories → Services → Routers
**Strategy:** Refactor entity by entity (complete one before next)

### Scenario B: Large Application
**Approach:** Incremental refactoring
**Strategy:**
1. Create structure alongside existing code
2. Refactor one module at a time
3. Keep application working throughout
4. Gradually migrate endpoints

### Scenario C: Complex Dependencies
**Approach:** Map dependencies first
**Strategy:**
1. Identify all inter-entity dependencies
2. Refactor independent entities first
3. Handle circular dependencies (rethink boundaries)
4. Use events for loose coupling if needed

## Reference Materials

**For detailed patterns and best practices:**
See `references/clean-architecture-patterns.md` for:
- Detailed layer responsibilities
- Design patterns (Repository, Service, DI)
- Error handling strategies
- Testing approaches
- Anti-patterns to avoid

**For step-by-step refactoring instructions:**
See `references/refactoring-guide.md` for:
- Complete refactoring process
- Phase-by-phase guide
- Migration strategies
- Common challenges and solutions
- Refactoring checklist

**For complete working example:**
See `assets/template-structure/` for:
- Complete folder structure
- Example files for each layer
- Dependency injection setup
- Database configuration
- Two complete entities (User, Item)

## Refactoring Checklist

Before starting:
- [ ] Understand current structure
- [ ] Identify all entities
- [ ] Map dependencies between entities

During refactoring:
- [ ] Create folder structure
- [ ] Setup core configuration
- [ ] Extract models (DB + Pydantic)
- [ ] Create base repository
- [ ] Create entity repositories
- [ ] Create entity services
- [ ] Setup dependency injection
- [ ] Refactor route handlers
- [ ] Register routers

After refactoring:
- [ ] Test all endpoints
- [ ] Verify no circular imports
- [ ] Check dependency direction
- [ ] Update tests
- [ ] Update documentation

## Best Practices

1. **Refactor incrementally** - Complete one entity before moving to next
2. **Keep it working** - Application should run after each phase
3. **Consistent naming** - Use same patterns for all entities
4. **Type hints everywhere** - Better IDE support and error catching
5. **Single responsibility** - Each layer, class, method has one purpose
6. **Dependency injection** - Use FastAPI's Depends consistently
7. **Test as you go** - Add tests while refactoring
8. **Document decisions** - Add docstrings to complex methods

## Common Mistakes to Avoid

❌ Database queries in routes
❌ Business logic in repositories
❌ Repositories calling services
❌ Services depending on routers
❌ Missing type hints
❌ Inconsistent naming conventions
❌ Skipping dependency injection
❌ Not testing after refactoring

## Support for Different Scales

**Small App (1-3 entities):**
- Can complete refactoring in one session
- Refactor all at once
- Simple dependency structure

**Medium App (4-10 entities):**
- Refactor entity by entity
- May take multiple sessions
- Watch for shared logic

**Large App (10+ entities):**
- Incremental refactoring essential
- Group related entities
- Consider bounded contexts
- May need additional patterns (CQRS, Event Sourcing)
