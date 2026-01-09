# Clean Architecture Patterns for FastAPI

## Core Principles

### 1. Dependency Direction
Dependencies flow inward: **Routers → Services → Repositories → Database**

```
Routers (Presentation)
    ↓
Services (Business Logic)
    ↓
Repositories (Data Access)
    ↓
Database
```

**Rules:**
- Routers depend on Services (never directly on Repositories)
- Services depend on Repositories
- Repositories depend on Database models
- Lower layers NEVER know about upper layers

### 2. Layer Responsibilities

#### Routers (Presentation Layer)
**Purpose:** Handle HTTP concerns only

**Responsibilities:**
- Receive HTTP requests
- Validate request data (FastAPI does this automatically)
- Call service methods
- Return HTTP responses with appropriate status codes
- Handle authentication/authorization tokens

**Should NOT:**
- Contain business logic
- Access database directly
- Implement validation logic (use Pydantic)
- Handle complex error transformations

**Example:**
```python
@router.post("/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, service: UserServiceDep):
    """Create endpoint - delegates to service"""
    return service.create_user(user)
```

#### Services (Business Logic Layer)
**Purpose:** Implement business rules and orchestrate operations

**Responsibilities:**
- Validate business rules (not just data format)
- Coordinate multiple repository calls
- Transform data between layers
- Implement complex workflows
- Raise business exceptions (HTTPException)
- Handle transactions

**Should NOT:**
- Know about HTTP requests/responses
- Construct database queries
- Know about database implementation details

**Example:**
```python
def create_user(self, user_data: UserCreate) -> UserResponse:
    # Business rule: check uniqueness
    if self.repository.email_exists(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Business logic: hash password
    hashed_password = pwd_context.hash(user_data.password)

    # Create via repository
    user = UserDB(email=user_data.email, hashed_password=hashed_password)
    created_user = self.repository.create(user)

    # Return API model
    return UserResponse.model_validate(created_user)
```

#### Repositories (Data Access Layer)
**Purpose:** Encapsulate database operations

**Responsibilities:**
- CRUD operations
- Database queries
- Filtering and pagination
- Joins and aggregations
- Return database models

**Should NOT:**
- Contain business logic
- Validate business rules
- Raise business exceptions (only DB errors)
- Transform to API models

**Example:**
```python
def get_by_email(self, email: str) -> Optional[UserDB]:
    """Simple query - no business logic"""
    return self.db.query(UserDB).filter(UserDB.email == email).first()
```

#### Models
**Purpose:** Define data structures

**Two types:**
1. **Database Models** (SQLAlchemy): Represent database tables
2. **API Schemas** (Pydantic): Represent API request/response

**Example:**
```python
# Database Model
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)

# API Schemas
class UserCreate(BaseModel):  # Request
    email: EmailStr
    password: str

class UserResponse(BaseModel):  # Response
    id: int
    email: EmailStr
```

## Design Patterns

### 1. Dependency Injection Pattern

**Setup in core/dependencies.py:**
```python
# Database dependency
DatabaseDep = Annotated[Session, Depends(get_db)]

# Repository dependencies
def get_user_repository(db: DatabaseDep) -> UserRepository:
    return UserRepository(db)

UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]

# Service dependencies
def get_user_service(repository: UserRepositoryDep) -> UserService:
    return UserService(repository)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
```

**Use in routers:**
```python
@router.get("/")
def get_users(service: UserServiceDep):
    return service.get_users()
```

### 2. Repository Pattern

**Base repository with generics:**
```python
class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()
```

**Specific repository extends base:**
```python
class UserRepository(BaseRepository[UserDB]):
    def __init__(self, db: Session):
        super().__init__(UserDB, db)

    def get_by_email(self, email: str) -> Optional[UserDB]:
        return self.db.query(UserDB).filter(UserDB.email == email).first()
```

### 3. Service Pattern

**Service receives repository via constructor:**
```python
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user_data: UserCreate) -> UserResponse:
        # Business logic here
        # Calls repository methods
        pass
```

### 4. Error Handling

**Hierarchy:**
- **Routers**: Don't catch errors (let FastAPI handle them)
- **Services**: Raise HTTPException for business rule violations
- **Repositories**: Let database errors propagate or raise generic errors

**Example:**
```python
# Service
def create_user(self, user_data: UserCreate) -> UserResponse:
    if self.repository.email_exists(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    # ...
```

## Common Patterns

### Pattern: Create Operation
1. **Router** receives request data
2. **Service** validates business rules
3. **Service** creates database model
4. **Repository** persists to database
5. **Service** transforms to response schema
6. **Router** returns response

### Pattern: Update Operation
1. **Router** receives ID + update data
2. **Service** fetches existing entity via repository
3. **Service** validates business rules
4. **Service** updates entity fields
5. **Repository** saves changes
6. **Service** returns updated schema

### Pattern: Complex Query
1. **Router** receives query parameters
2. **Service** orchestrates multiple repository calls if needed
3. **Repository** executes database queries
4. **Service** combines/transforms results
5. **Router** returns combined response

## Testing Strategy

### Unit Tests by Layer

**Repositories:**
- Test with real/in-memory database
- Verify CRUD operations
- Test custom queries

**Services:**
- Mock repositories
- Test business logic
- Test error conditions

**Routers:**
- Use TestClient
- Test HTTP layer
- Test status codes and response formats

**Example:**
```python
# Test service with mocked repository
def test_create_user_duplicate_email():
    mock_repo = Mock(spec=UserRepository)
    mock_repo.email_exists.return_value = True

    service = UserService(mock_repo)

    with pytest.raises(HTTPException) as exc:
        service.create_user(UserCreate(email="test@test.com", password="pass"))

    assert exc.value.status_code == 400
```

## Migration from Monolithic

### Step 1: Extract Models
Move Pydantic schemas and database models to `models/`

### Step 2: Create Repositories
Extract all database queries into repository methods

### Step 3: Create Services
Move business logic from routes into service methods

### Step 4: Refactor Routers
Slim down route handlers to just HTTP handling

### Step 5: Setup Dependencies
Configure dependency injection in `core/dependencies.py`

## Anti-Patterns to Avoid

❌ **Router queries database directly**
```python
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()  # Wrong!
```

❌ **Service contains HTTP details**
```python
def create_user(self, request: Request):  # Wrong!
    # Service shouldn't know about Request
```

❌ **Repository contains business logic**
```python
def create_user(self, email: str):
    if self.email_exists(email):  # Wrong! This is business logic
        raise ValueError("Email exists")
```

❌ **Circular dependencies**
```python
# UserService imports ItemService
# ItemService imports UserService  # Wrong!
```

## Benefits

✅ **Separation of Concerns**: Each layer has clear responsibility
✅ **Testability**: Easy to mock dependencies
✅ **Maintainability**: Changes isolated to specific layers
✅ **Scalability**: Easy to add new features
✅ **Flexibility**: Easy to swap implementations (e.g., change database)
