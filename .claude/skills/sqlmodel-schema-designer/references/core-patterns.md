# SQLModel Core Patterns

## Table of Contents
- Relationships (One-to-Many, Many-to-Many)
- Enums with SQLModel
- Timestamps (created_at, updated_at)
- Indexes (Single, Composite, Unique)

## Relationships

### One-to-Many

```python
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List

class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)

    # Relationship
    books: List["Book"] = Relationship(back_populates="author")

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author_id: Optional[int] = Field(default=None, foreign_key="author.id")

    # Relationship
    author: Optional[Author] = Relationship(back_populates="books")
```

### Many-to-Many (with Link Table)

```python
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List

class StudentCourseLink(SQLModel, table=True):
    student_id: Optional[int] = Field(default=None, foreign_key="student.id", primary_key=True)
    course_id: Optional[int] = Field(default=None, foreign_key="course.id", primary_key=True)

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    courses: List["Course"] = Relationship(back_populates="students", link_model=StudentCourseLink)

class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    students: List[Student] = Relationship(back_populates="courses", link_model=StudentCourseLink)
```

### Many-to-Many (with Additional Fields)

```python
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List

class Enrollment(SQLModel, table=True):
    student_id: Optional[int] = Field(default=None, foreign_key="student.id", primary_key=True)
    course_id: Optional[int] = Field(default=None, foreign_key="course.id", primary_key=True)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    grade: Optional[str] = None

    student: "Student" = Relationship(back_populates="enrollments")
    course: "Course" = Relationship(back_populates="enrollments")

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    enrollments: List[Enrollment] = Relationship(back_populates="student")

class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str

    enrollments: List[Enrollment] = Relationship(back_populates="course")
```

## Enums

### Using Python Enum with SQLModel

```python
from enum import Enum
from sqlmodel import Field, SQLModel
from typing import Optional

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_number: str = Field(unique=True, index=True)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
```

### Multiple Enums in a Model

```python
from enum import Enum
from sqlmodel import Field, SQLModel
from typing import Optional

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    method: PaymentMethod
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
```

## Timestamps

### Basic Timestamps

```python
from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Timestamps with sa_column for Database Defaults

```python
from datetime import datetime
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import DateTime, func
from typing import Optional

class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
```

## Indexes

### Single Column Index

```python
from sqlmodel import Field, SQLModel
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(index=True)
```

### Composite Index

```python
from sqlmodel import Field, SQLModel
from sqlalchemy import Index
from typing import Optional

class Product(SQLModel, table=True):
    __table_args__ = (
        Index('idx_category_price', 'category', 'price'),
        Index('idx_brand_status', 'brand', 'status'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    brand: str
    price: float
    status: str
```

### Unique Composite Index

```python
from sqlmodel import Field, SQLModel
from sqlalchemy import Index
from typing import Optional

class UserProfile(SQLModel, table=True):
    __table_args__ = (
        Index('idx_user_platform', 'user_id', 'platform', unique=True),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int
    platform: str
    profile_data: str
```

### Partial Index (PostgreSQL)

```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Index, String
from typing import Optional

class Task(SQLModel, table=True):
    __table_args__ = (
        Index('idx_active_tasks', 'status', postgresql_where=(Column('status') == 'active')),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    status: str
```
