# SQLModel Advanced Features

## Table of Contents
- Soft Deletes
- UUID Primary Keys
- Pydantic Validators
- Full-Text Search (PostgreSQL)

## Soft Deletes

### Basic Soft Delete Pattern

```python
from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str

    # Soft delete fields
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None
```

### Soft Delete with Deletion Metadata

```python
from datetime import datetime
from sqlmodel import Field, SQLModel
from typing import Optional

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    sku: str = Field(unique=True, index=True)

    # Soft delete with metadata
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = Field(default=None, foreign_key="user.id")
    deletion_reason: Optional[str] = None
```

### Composite Index for Active Records

```python
from datetime import datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import Index
from typing import Optional

class Article(SQLModel, table=True):
    __table_args__ = (
        # Index for querying active articles by category
        Index('idx_active_category', 'category', 'is_deleted'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    category: str

    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None
```

## UUID Primary Keys

### Basic UUID Pattern

```python
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel
from typing import Optional

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
```

### UUID with String Storage (SQLite compatible)

```python
from uuid import uuid4
from sqlmodel import Field, SQLModel
from typing import Optional

class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
```

### UUID Foreign Keys

```python
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List

class Author(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str

    books: List["Book"] = Relationship(back_populates="author")

class Book(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str
    author_id: UUID = Field(foreign_key="author.id")

    author: Author = Relationship(back_populates="books")
```

### UUID with Database Default (PostgreSQL)

```python
from uuid import UUID
from sqlmodel import Field, SQLModel, Column
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy import text

class User(SQLModel, table=True):
    id: UUID = Field(
        sa_column=Column(
            PostgreSQLUUID(as_uuid=True),
            primary_key=True,
            server_default=text("gen_random_uuid()")
        )
    )
    email: str = Field(unique=True, index=True)
    name: str
```

## Pydantic Validators

### Email Validation

```python
from sqlmodel import Field, SQLModel
from pydantic import EmailStr, field_validator
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    name: str

    @field_validator('email')
    @classmethod
    def email_must_be_lowercase(cls, v: str) -> str:
        return v.lower()
```

### String Length and Pattern Validation

```python
import re
from sqlmodel import Field, SQLModel
from pydantic import field_validator
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(min_length=3, max_length=20, index=True)
    phone: Optional[str] = None

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric with underscores only')
        return v

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        # Simple US phone validation
        pattern = r'^\+?1?\d{10}$'
        if not re.match(pattern, v.replace('-', '').replace(' ', '')):
            raise ValueError('Invalid phone number format')
        return v
```

### Numeric Range Validation

```python
from sqlmodel import Field, SQLModel
from pydantic import field_validator
from typing import Optional

class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float = Field(gt=0)  # Greater than 0
    discount_percent: float = Field(ge=0, le=100)  # Between 0 and 100
    stock: int = Field(ge=0)  # Greater than or equal to 0

    @field_validator('price')
    @classmethod
    def validate_price_precision(cls, v: float) -> float:
        # Ensure max 2 decimal places
        return round(v, 2)
```

### URL and Custom Validators

```python
from sqlmodel import Field, SQLModel
from pydantic import HttpUrl, field_validator
from typing import Optional

class Website(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    url: HttpUrl
    slug: str = Field(unique=True, index=True)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        # Convert to lowercase and replace spaces with hyphens
        return v.lower().replace(' ', '-').replace('_', '-')

    @field_validator('url')
    @classmethod
    def validate_url_https(cls, v: str) -> str:
        if not v.startswith('https://'):
            raise ValueError('URL must use HTTPS')
        return v
```

### Cross-Field Validation

```python
from datetime import datetime
from sqlmodel import Field, SQLModel
from pydantic import model_validator
from typing import Optional

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    start_date: datetime
    end_date: datetime

    @model_validator(mode='after')
    def validate_dates(self):
        if self.end_date <= self.start_date:
            raise ValueError('end_date must be after start_date')
        return self
```

## Full-Text Search (PostgreSQL)

### Basic Full-Text Search with TSVector

```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Index, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from typing import Optional

class Article(SQLModel, table=True):
    __table_args__ = (
        Index('idx_article_search', 'search_vector', postgresql_using='gin'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    search_vector: Optional[str] = Field(
        sa_column=Column(TSVECTOR)
    )
```

### Full-Text Search with Generated Column

```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Index, text
from sqlalchemy.dialects.postgresql import TSVECTOR
from typing import Optional

class Post(SQLModel, table=True):
    __table_args__ = (
        Index('idx_post_search', 'search_vector', postgresql_using='gin'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    search_vector: Optional[str] = Field(
        sa_column=Column(
            TSVECTOR,
            # Auto-generated from title and content
            server_default=text(
                "to_tsvector('english', coalesce(title, '') || ' ' || coalesce(content, ''))"
            )
        )
    )
```

### Full-Text Search with Weighted Ranking

```python
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import Index, text
from sqlalchemy.dialects.postgresql import TSVECTOR
from typing import Optional

class Document(SQLModel, table=True):
    __table_args__ = (
        Index('idx_document_search', 'search_vector', postgresql_using='gin'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    subtitle: Optional[str] = None
    content: str
    tags: Optional[str] = None

    # Weighted search: title (A), subtitle (B), content (C), tags (D)
    search_vector: Optional[str] = Field(
        sa_column=Column(
            TSVECTOR,
            server_default=text("""
                setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(subtitle, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(content, '')), 'C') ||
                setweight(to_tsvector('english', coalesce(tags, '')), 'D')
            """)
        )
    )
```

### Querying with Full-Text Search

```python
# Example query usage (not part of model definition)
from sqlmodel import select, Session
from sqlalchemy import func

# Basic search
def search_articles(session: Session, query: str):
    statement = select(Article).where(
        Article.search_vector.op('@@')(func.plainto_tsquery('english', query))
    )
    return session.exec(statement).all()

# Ranked search with scoring
def search_articles_ranked(session: Session, query: str):
    tsquery = func.plainto_tsquery('english', query)
    rank = func.ts_rank(Article.search_vector, tsquery)

    statement = select(Article, rank.label('rank')).where(
        Article.search_vector.op('@@')(tsquery)
    ).order_by(rank.desc())

    return session.exec(statement).all()
```
