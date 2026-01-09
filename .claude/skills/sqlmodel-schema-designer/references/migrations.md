# Alembic Migrations for SQLModel

## Table of Contents
- Setup and Configuration
- Creating Migrations
- Common Migration Operations
- Best Practices

## Setup and Configuration

### Initial Setup

```bash
# Install Alembic
pip install alembic

# Initialize Alembic in your project
alembic init alembic
```

### Configure alembic.ini

```ini
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:pass@localhost/dbname

# Alternatively, set URL from environment variable
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

### Configure env.py for SQLModel

```python
# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlmodel import SQLModel

# Import all your models here
from app.models import User, Post, Comment  # Your models

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata from SQLModel
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### Using Environment Variables

```python
# alembic/env.py (alternative with environment variables)
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from sqlmodel import SQLModel

config = context.config

# Override sqlalchemy.url from environment variable
config.set_main_option(
    'sqlalchemy.url',
    os.getenv('DATABASE_URL', 'postgresql://localhost/mydb')
)

# ... rest of configuration
```

## Creating Migrations

### Auto-generate Migration

```bash
# Create a new migration with auto-detected changes
alembic revision --autogenerate -m "Add user table"

# Review the generated file in alembic/versions/
```

### Manual Migration

```bash
# Create an empty migration file
alembic revision -m "Add custom index"
```

### Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply migrations up to a specific revision
alembic upgrade abc123

# Rollback one migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

## Common Migration Operations

### Creating a Table

```python
# alembic/versions/xxx_create_user_table.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)

def downgrade() -> None:
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
```

### Adding/Removing Columns

```python
def upgrade() -> None:
    # Add column
    op.add_column('user', sa.Column('phone', sa.String(), nullable=True))

    # Add column with default value
    op.add_column(
        'user',
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False)
    )

def downgrade() -> None:
    op.drop_column('user', 'phone')
    op.drop_column('user', 'is_active')
```

### Modifying Columns

```python
def upgrade() -> None:
    # Change column type
    op.alter_column('user', 'age',
        existing_type=sa.Integer(),
        type_=sa.BigInteger(),
        existing_nullable=True
    )

    # Make column nullable/not nullable
    op.alter_column('user', 'email',
        existing_type=sa.String(),
        nullable=False
    )

    # Rename column
    op.alter_column('user', 'user_name', new_column_name='username')

def downgrade() -> None:
    op.alter_column('user', 'age',
        existing_type=sa.BigInteger(),
        type_=sa.Integer(),
        existing_nullable=True
    )
    op.alter_column('user', 'email',
        existing_type=sa.String(),
        nullable=True
    )
    op.alter_column('user', 'username', new_column_name='user_name')
```

### Creating Indexes

```python
def upgrade() -> None:
    # Simple index
    op.create_index('idx_user_username', 'user', ['username'])

    # Unique index
    op.create_index('idx_user_email', 'user', ['email'], unique=True)

    # Composite index
    op.create_index('idx_user_name_email', 'user', ['name', 'email'])

    # Partial index (PostgreSQL)
    op.create_index(
        'idx_active_users',
        'user',
        ['status'],
        postgresql_where=sa.text("status = 'active'")
    )

def downgrade() -> None:
    op.drop_index('idx_user_username', table_name='user')
    op.drop_index('idx_user_email', table_name='user')
    op.drop_index('idx_user_name_email', table_name='user')
    op.drop_index('idx_active_users', table_name='user')
```

### Foreign Keys

```python
def upgrade() -> None:
    # Add foreign key
    op.create_foreign_key(
        'fk_post_author_id',
        'post', 'user',
        ['author_id'], ['id'],
        ondelete='CASCADE'
    )

def downgrade() -> None:
    op.drop_constraint('fk_post_author_id', 'post', type_='foreignkey')
```

### Adding Enums (PostgreSQL)

```python
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Create enum type
    order_status = sa.Enum('pending', 'processing', 'shipped', 'delivered', name='orderstatus')
    order_status.create(op.get_bind(), checkfirst=True)

    # Use in table
    op.create_table(
        'order',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'processing', 'shipped', 'delivered', name='orderstatus')),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('order')
    # Drop enum type
    sa.Enum(name='orderstatus').drop(op.get_bind(), checkfirst=True)
```

### Data Migration

```python
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

def upgrade() -> None:
    # Define temporary table representation
    user_table = table('user',
        column('id', sa.Integer),
        column('status', sa.String)
    )

    # Update existing data
    op.execute(
        user_table.update().
        where(user_table.c.status == None).
        values(status='active')
    )

def downgrade() -> None:
    # Reverse data changes if needed
    pass
```

## Best Practices

### 1. Always Review Auto-generated Migrations

Auto-generated migrations may not always be perfect. Review and adjust:
- Check for unwanted table drops
- Verify data type changes
- Ensure indexes are created correctly

### 2. Test Migrations on Development First

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test full cycle
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

### 3. Use Meaningful Migration Messages

```bash
# Good
alembic revision --autogenerate -m "Add user authentication tables"

# Bad
alembic revision --autogenerate -m "Update"
```

### 4. Handle Data Migrations Carefully

```python
def upgrade() -> None:
    # Add column with default
    op.add_column('user', sa.Column('status', sa.String(), nullable=True))

    # Migrate existing data
    op.execute("UPDATE user SET status = 'active' WHERE status IS NULL")

    # Make column non-nullable after data migration
    op.alter_column('user', 'status', nullable=False)
```

### 5. Use Batch Operations for SQLite

```python
def upgrade() -> None:
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('phone', sa.String()))
        batch_op.alter_column('email', nullable=False)
```

### 6. Keep Migrations Small and Focused

Create separate migrations for:
- Schema changes
- Data migrations
- Index additions

This makes rollbacks easier and debugging simpler.

### 7. Document Complex Migrations

```python
"""Add user authentication and profile tables

Revision ID: abc123
Revises: def456
Create Date: 2024-01-09

This migration adds:
- user authentication table with email/password
- user profile table with additional details
- indexes for email lookup
"""

def upgrade() -> None:
    # Implementation
    pass
```
