---
name: sqlmodel-schema-designer
description: "Generate production-ready SQLModel database schemas from entity descriptions. Use when users request database models, schemas, or table definitions with any of the following: SQLModel, SQLAlchemy, FastAPI with databases, relationships (one-to-many, many-to-many), enums, timestamps, indexes, soft deletes, UUID primary keys, validators, or full-text search. Triggers include phrases like 'create models for', 'design schema for', 'generate SQLModel classes', 'database structure for', or when describing entities like 'User and Post with relationships'."
---

# SQLModel Schema Designer

## Overview

Generate complete, production-ready SQLModel classes from natural language entity descriptions. Automatically includes relationships, enums, timestamps, indexes, validators, and advanced features like soft deletes, UUID primary keys, and PostgreSQL full-text search.

## Workflow

### 1. Gather Requirements

First, understand the schema requirements by asking about output preferences:

- **Detail level**: Full implementation with all features, or basic structure for user customization
- **Primary key type**: Auto-increment integers or UUIDs
- **Optional features**: Soft deletes, validators, full-text search

Use this question format:

```
I'll generate SQLModel classes for [entities]. What level of detail would you like?

1. Full implementation (Recommended) - Complete classes with all imports, type hints, validators, and configuration
2. Basic structure - Core models with minimal configuration, you add details later
```

### 2. Generate Schema

Based on the requirements, generate SQLModel classes following these principles:

**Required Elements:**
- Proper imports (SQLModel, Field, Relationship, Optional, List, etc.)
- Table definitions with `table=True`
- Primary keys with appropriate types
- Foreign keys for relationships
- Relationship definitions with `back_populates`

**Include When Specified:**
- Enums for status fields or categorical data
- Timestamps (`created_at`, `updated_at`) using `sa_column` with `server_default=func.now()`
- Indexes for foreign keys, frequently queried fields, and unique constraints
- Soft delete fields (`is_deleted`, `deleted_at`) with indexes
- UUID primary keys with `default_factory=uuid4`
- Pydantic validators for email, phone, URLs, etc.
- Full-text search with TSVector columns and GIN indexes

### 3. Reference Patterns

Load reference files as needed:

**Core patterns** - See [core-patterns.md](references/core-patterns.md) for:
- Relationships (one-to-many, many-to-many)
- Enums with SQLModel
- Timestamps with database defaults
- Indexes (single, composite, unique, partial)

**Advanced features** - See [advanced-features.md](references/advanced-features.md) for:
- Soft delete patterns with metadata
- UUID primary keys (native, string-based, PostgreSQL)
- Pydantic validators (email, phone, URL, custom)
- Full-text search with weighted ranking

**Complete examples** - See [examples.md](references/examples.md) for:
- E-commerce system (Product, Order, Customer)
- Blog platform (User, Post, Comment, Tag)
- Multi-tenant SaaS (Organization, Workspace, User)

**Migrations** - See [migrations.md](references/migrations.md) for:
- Alembic setup and configuration
- Creating and running migrations
- Common migration operations

### 4. Structure Output

Present the generated schema in this format:

```
# [System Name] SQLModel Schema

## Entities
- [List of entities with brief descriptions]

## Generated Models

[Complete Python code with all imports and classes]

## Database Setup

[Brief instructions for creating tables]

## Migration Guide

For Alembic migrations, see references/migrations.md
```

**Code organization:**
1. Imports at the top
2. Enums defined first
3. Link tables for many-to-many relationships
4. Main models in logical order (parent before child)

### 5. Explain Key Features

After generating the schema, briefly explain:

- **Relationships**: How entities connect (one-to-many, many-to-many)
- **Indexes**: Which fields are indexed and why
- **Timestamps**: Auto-updating created_at/updated_at behavior
- **Special features**: Soft deletes, UUIDs, validators, full-text search if included

## Common Patterns

### Relationship Patterns

**One-to-Many:**
```python
class Author(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    books: List["Book"] = Relationship(back_populates="author")

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author_id: Optional[int] = Field(foreign_key="author.id")
    author: Optional[Author] = Relationship(back_populates="books")
```

**Many-to-Many with Link Table:**
```python
class StudentCourseLink(SQLModel, table=True):
    student_id: Optional[int] = Field(foreign_key="student.id", primary_key=True)
    course_id: Optional[int] = Field(foreign_key="course.id", primary_key=True)

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    courses: List["Course"] = Relationship(back_populates="students", link_model=StudentCourseLink)
```

### Timestamp Pattern

```python
from datetime import datetime
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import DateTime, func

class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
```

### Enum Pattern

```python
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    status: OrderStatus = Field(default=OrderStatus.PENDING)
```

### Index Pattern

```python
from sqlalchemy import Index

class Product(SQLModel, table=True):
    __table_args__ = (
        Index('idx_category_price', 'category', 'price'),
        Index('idx_active_products', 'is_deleted', 'status'),
    )

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)  # Simple index
    sku: str = Field(unique=True, index=True)  # Unique index
    category: str
    price: float
    is_deleted: bool = Field(default=False)
    status: str
```

## Output Format Examples

### Full Implementation Example

When user requests full implementation, generate complete code with:
- All necessary imports
- Type hints and Optional types
- Validators for data integrity
- Comprehensive indexes
- Database-level defaults
- Detailed comments for complex patterns

### Basic Structure Example

When user requests basic structure, generate minimal code with:
- Essential imports only
- Basic type hints
- Primary/foreign keys
- Simple relationships
- Placeholders for additional features

## Best Practices

- **Use `Optional` types** for nullable foreign keys and optional fields
- **Index foreign keys** to improve join performance
- **Add composite indexes** for common query patterns (e.g., filtering by category + status)
- **Use `sa_column`** for database-level defaults on timestamps
- **Validate at boundaries** with Pydantic validators for user input
- **Use soft deletes** for data recovery and audit trails
- **Consider UUIDs** for distributed systems or public-facing IDs
- **Add full-text search** for content-heavy tables (articles, products)
- **Use enums** for fixed sets of values to enforce data integrity

## Resources

### references/core-patterns.md
Comprehensive examples of relationships, enums, timestamps, and indexes. Load when generating schemas with these features.

### references/advanced-features.md
Detailed patterns for soft deletes, UUID primary keys, Pydantic validators, and PostgreSQL full-text search. Load when users request advanced features.

### references/examples.md
Complete working examples of e-commerce, blog, and multi-tenant SaaS systems. Load when users need inspiration or want to see full implementations.

### references/migrations.md
Alembic setup and migration patterns. Reference when users ask about migrations, schema changes, or Alembic configuration.
