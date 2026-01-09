# FastAPI Clean Architecture Refactoring Guide

## Overview

This guide provides a systematic approach to refactoring monolithic FastAPI applications into clean architecture.

## Refactoring Process

### Phase 1: Analysis

**1.1 Identify Current Structure**
- Locate all route handlers
- Find database query locations
- Identify business logic locations
- Map data models

**1.2 Analyze Dependencies**
- Document which routes use which models
- Identify shared logic
- Find circular dependencies
- Note external integrations

**Questions to ask:**
- Where are database queries? (in routes, separate files, or mixed?)
- Is business logic in routes or separate functions?
- Are models defined in one place or scattered?
- How is database session managed?

### Phase 2: Preparation

**2.1 Create Folder Structure**
```bash
mkdir -p app/core
mkdir -p app/models
mkdir -p app/repositories
mkdir -p app/services
mkdir -p app/routers
```

**2.2 Setup Core Configuration**
Create `app/core/config.py`, `app/core/database.py`, and `app/core/dependencies.py`

**2.3 Install Dependencies**
```bash
pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings
```

### Phase 3: Extract Models

**3.1 Extract Database Models**
Move SQLAlchemy models to `models/` directory, one file per entity.

**Before:**
```python
# main.py
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    # ...
```

**After:**
```python
# models/user.py
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    # ...
```

**3.2 Create Pydantic Schemas**
Create API schemas (Create, Update, Response) in same model files.

```python
# models/user.py
class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
```

### Phase 4: Extract Repositories

**4.1 Create Base Repository**
Create `repositories/base_repository.py` with generic CRUD operations.

**4.2 Extract Database Queries**
Find all database queries in routes and move to repositories.

**Before:**
```python
# routes.py
@app.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404)
    return user
```

**After:**
```python
# repositories/user_repository.py
class UserRepository(BaseRepository[UserDB]):
    def __init__(self, db: Session):
        super().__init__(UserDB, db)

    def get(self, id: int) -> Optional[UserDB]:
        return self.db.query(UserDB).filter(UserDB.id == id).first()
```

**4.3 Group Related Queries**
Put all queries for an entity in its repository.

**Common repository methods:**
- `get(id)` - Get by ID
- `get_all(skip, limit)` - List with pagination
- `create(obj)` - Create new
- `update(obj)` - Update existing
- `delete(id)` - Delete by ID
- Custom queries (e.g., `get_by_email()`, `search()`)

### Phase 5: Extract Services

**5.1 Identify Business Logic**
Look for:
- Validation beyond data types
- Calculations and transformations
- Conditional logic
- Multiple repository calls
- Password hashing, token generation

**5.2 Create Service Classes**
One service per entity or bounded context.

**Before:**
```python
# routes.py
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email exists")

    # Hash password
    hashed = pwd_context.hash(user.password)

    # Create user
    db_user = User(email=user.email, hashed_password=hashed)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user
```

**After:**
```python
# services/user_service.py
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user_data: UserCreate) -> UserResponse:
        # Business logic: check uniqueness
        if self.repository.email_exists(user_data.email):
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        # Business logic: hash password
        hashed_password = pwd_context.hash(user_data.password)

        # Create via repository
        user = UserDB(
            email=user_data.email,
            hashed_password=hashed_password
        )
        created_user = self.repository.create(user)

        # Transform to response
        return UserResponse.model_validate(created_user)
```

**5.3 Service Method Pattern**
```python
def service_method(self, input_data: InputSchema) -> OutputSchema:
    # 1. Validate business rules
    # 2. Fetch data via repository
    # 3. Apply business logic
    # 4. Call repository to persist
    # 5. Transform to output schema
    # 6. Return result
```

### Phase 6: Refactor Routers

**6.1 Setup Dependency Injection**
Create dependencies in `core/dependencies.py`:

```python
# core/dependencies.py
def get_user_repository(db: DatabaseDep) -> UserRepository:
    return UserRepository(db)

def get_user_service(repository: UserRepositoryDep) -> UserService:
    return UserService(repository)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
```

**6.2 Slim Down Route Handlers**
Routes should only:
- Receive request
- Call service
- Return response

**Before:**
```python
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # 30 lines of business logic and database queries
    pass
```

**After:**
```python
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, service: UserServiceDep):
    return service.create_user(user)
```

**6.3 Organize Routes by Entity**
Create one router file per entity or feature.

```python
# routers/users.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_users(service: UserServiceDep):
    return service.get_users()

@router.post("/")
def create_user(user: UserCreate, service: UserServiceDep):
    return service.create_user(user)
```

**6.4 Register Routers in Main**
```python
# main.py
from app.routers import users, items

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(items.router, prefix="/api/v1/items", tags=["items"])
```

### Phase 7: Testing

**7.1 Update Tests**
Update tests to match new structure:

**Repository tests:**
```python
def test_user_repository_get(db_session):
    repo = UserRepository(db_session)
    user = repo.get(1)
    assert user.id == 1
```

**Service tests (with mocked repository):**
```python
def test_create_user_duplicate_email():
    mock_repo = Mock(spec=UserRepository)
    mock_repo.email_exists.return_value = True

    service = UserService(mock_repo)

    with pytest.raises(HTTPException):
        service.create_user(UserCreate(email="test@test.com"))
```

**Router tests:**
```python
def test_create_user_endpoint(client):
    response = client.post("/api/v1/users", json={
        "email": "test@test.com",
        "username": "test",
        "password": "pass123"
    })
    assert response.status_code == 201
```

### Phase 8: Verification

**8.1 Verify All Endpoints Work**
- Test each endpoint manually or with Postman
- Check database operations
- Verify error handling

**8.2 Check Dependencies**
- No circular imports
- All dependencies properly injected
- No direct database access in routes

**8.3 Review Code Quality**
- Consistent naming conventions
- Proper type hints
- Clear separation of concerns

## Incremental Refactoring Strategy

**For large applications**, refactor incrementally:

### Strategy 1: By Entity
1. Refactor User entity completely (models → repos → services → routes)
2. Refactor Item entity
3. Continue with remaining entities

### Strategy 2: By Layer
1. Extract all models first
2. Create all repositories
3. Create all services
4. Refactor all routers

### Strategy 3: By Feature
1. Refactor authentication feature
2. Refactor user management
3. Continue with remaining features

**Recommendation:** Strategy 1 (by entity) is usually safest for maintaining working application during refactoring.

## Migration Checklist

- [ ] Create folder structure
- [ ] Setup core configuration (config.py, database.py)
- [ ] Extract database models to `models/`
- [ ] Create Pydantic schemas in `models/`
- [ ] Create base repository
- [ ] Extract database queries to repositories
- [ ] Create service classes
- [ ] Extract business logic to services
- [ ] Setup dependency injection
- [ ] Refactor route handlers
- [ ] Update tests
- [ ] Verify all endpoints
- [ ] Check for circular imports
- [ ] Update documentation

## Common Challenges

### Challenge 1: Circular Dependencies
**Problem:** ServiceA needs ServiceB, ServiceB needs ServiceA

**Solution:**
- Rethink service boundaries
- Create a shared service for common logic
- Use events/message passing
- Combine services if they're too coupled

### Challenge 2: Complex Transactions
**Problem:** Operation spans multiple repositories

**Solution:**
- Handle transaction in service layer
- Pass database session to repositories
- Use Unit of Work pattern if needed

```python
def transfer_item(self, item_id: int, from_user: int, to_user: int):
    # Both operations in same transaction
    item = self.item_repo.get(item_id)
    item.owner_id = to_user
    self.item_repo.update(item)

    # If any fails, both rollback automatically
    self.user_repo.update_item_count(from_user, -1)
    self.user_repo.update_item_count(to_user, 1)
```

### Challenge 3: Nested Dependencies
**Problem:** Service needs multiple repositories

**Solution:**
- Create dependencies for each repository
- Inject multiple repositories into service

```python
class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        item_repo: ItemRepository,
        user_repo: UserRepository
    ):
        self.order_repo = order_repo
        self.item_repo = item_repo
        self.user_repo = user_repo
```

### Challenge 4: Shared Logic
**Problem:** Multiple services need same logic

**Solution:**
- Create utility modules in `core/utils.py`
- Create shared service for common operations
- Use composition over inheritance

## Best Practices

1. **Start small**: Refactor one entity completely before moving to next
2. **Keep it working**: Ensure application runs after each step
3. **Write tests**: Add tests as you refactor
4. **Consistent naming**: Use same pattern for all files (user_service.py, item_service.py)
5. **Type hints**: Use type hints everywhere for better IDE support
6. **Document**: Add docstrings to service methods
7. **Review**: Code review each refactored component

## Example: Complete Refactoring

See `assets/template-structure/` for complete example of clean architecture with:
- Proper folder structure
- Database and API models
- Base repository with generic CRUD
- Specific repositories with custom queries
- Services with business logic
- Routers with dependency injection
- Configuration and setup
