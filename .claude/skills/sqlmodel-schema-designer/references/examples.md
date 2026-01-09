# Complete SQLModel Examples

## Table of Contents
- E-commerce System
- Blog System
- Multi-tenant SaaS

## E-commerce System

Complete e-commerce schema with products, orders, and customers.

```python
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import Index, DateTime, func
from pydantic import EmailStr, field_validator

# Enums
class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

# Models
class Customer(SQLModel, table=True):
    __table_args__ = (
        Index('idx_customer_email', 'email'),
        Index('idx_customer_active', 'is_deleted', 'email'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    first_name: str
    last_name: str
    phone: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    # Soft delete
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None

    # Relationships
    orders: List["Order"] = Relationship(back_populates="customer")
    addresses: List["Address"] = Relationship(back_populates="customer")

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.lower()

class Address(SQLModel, table=True):
    __table_args__ = (
        Index('idx_address_customer', 'customer_id'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    customer_id: UUID = Field(foreign_key="customer.id")
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    customer: Customer = Relationship(back_populates="addresses")

class Product(SQLModel, table=True):
    __table_args__ = (
        Index('idx_product_sku', 'sku'),
        Index('idx_product_status', 'status', 'is_deleted'),
        Index('idx_product_category_price', 'category', 'price'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    sku: str = Field(unique=True, index=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    category: str = Field(index=True)
    price: float = Field(gt=0)
    stock_quantity: int = Field(ge=0)
    status: ProductStatus = Field(default=ProductStatus.ACTIVE)

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    # Soft delete
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None

    # Relationships
    order_items: List["OrderItem"] = Relationship(back_populates="product")

    @field_validator('price')
    @classmethod
    def validate_price_precision(cls, v: float) -> float:
        return round(v, 2)

class Order(SQLModel, table=True):
    __table_args__ = (
        Index('idx_order_customer', 'customer_id'),
        Index('idx_order_status', 'status'),
        Index('idx_order_date', 'order_date'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_number: str = Field(unique=True, index=True)
    customer_id: UUID = Field(foreign_key="customer.id")
    status: OrderStatus = Field(default=OrderStatus.PENDING)

    # Order details
    subtotal: float = Field(ge=0)
    tax: float = Field(ge=0)
    shipping: float = Field(ge=0)
    total: float = Field(ge=0)

    # Timestamps
    order_date: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    shipped_date: Optional[datetime] = None
    delivered_date: Optional[datetime] = None

    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    # Relationships
    customer: Customer = Relationship(back_populates="orders")
    items: List["OrderItem"] = Relationship(back_populates="order")
    payment: Optional["Payment"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    __table_args__ = (
        Index('idx_orderitem_order', 'order_id'),
        Index('idx_orderitem_product', 'product_id'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id: UUID = Field(foreign_key="order.id")
    product_id: UUID = Field(foreign_key="product.id")
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    subtotal: float = Field(ge=0)

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    order: Order = Relationship(back_populates="items")
    product: Product = Relationship(back_populates="order_items")

class Payment(SQLModel, table=True):
    __table_args__ = (
        Index('idx_payment_order', 'order_id'),
        Index('idx_payment_status', 'status'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id: UUID = Field(foreign_key="order.id", unique=True)
    amount: float = Field(gt=0)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    payment_method: str
    transaction_id: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    processed_at: Optional[datetime] = None

    # Relationship
    order: Order = Relationship(back_populates="payment")

    @field_validator('amount')
    @classmethod
    def validate_amount_precision(cls, v: float) -> float:
        return round(v, 2)
```

## Blog System

Complete blog platform with users, posts, comments, and tags.

```python
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import Index, DateTime, func, text
from sqlalchemy.dialects.postgresql import TSVECTOR
from pydantic import EmailStr, field_validator
import re

# Enums
class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class UserRole(str, Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    AUTHOR = "author"
    READER = "reader"

# Link tables
class PostTagLink(SQLModel, table=True):
    post_id: UUID = Field(foreign_key="post.id", primary_key=True)
    tag_id: UUID = Field(foreign_key="tag.id", primary_key=True)

# Models
class User(SQLModel, table=True):
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
        Index('idx_user_role', 'role'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=30)
    full_name: str
    bio: Optional[str] = None
    role: UserRole = Field(default=UserRole.READER)

    # Authentication
    hashed_password: str
    is_active: bool = Field(default=True)

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
    last_login: Optional[datetime] = None

    # Soft delete
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None

    # Relationships
    posts: List["Post"] = Relationship(back_populates="author")
    comments: List["Comment"] = Relationship(back_populates="author")

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.lower()

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must be alphanumeric with underscores only')
        return v.lower()

class Post(SQLModel, table=True):
    __table_args__ = (
        Index('idx_post_author', 'author_id'),
        Index('idx_post_slug', 'slug'),
        Index('idx_post_status', 'status', 'is_deleted'),
        Index('idx_post_published', 'published_at'),
        Index('idx_post_search', 'search_vector', postgresql_using='gin'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(index=True)
    slug: str = Field(unique=True, index=True)
    content: str
    excerpt: Optional[str] = None
    author_id: UUID = Field(foreign_key="user.id")
    status: PostStatus = Field(default=PostStatus.DRAFT)
    view_count: int = Field(default=0, ge=0)

    # SEO
    meta_description: Optional[str] = None

    # Full-text search
    search_vector: Optional[str] = Field(
        sa_column=Column(
            TSVECTOR,
            server_default=text("""
                setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(excerpt, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(content, '')), 'C')
            """)
        )
    )

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
    published_at: Optional[datetime] = None

    # Soft delete
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None

    # Relationships
    author: User = Relationship(back_populates="posts")
    comments: List["Comment"] = Relationship(back_populates="post")
    tags: List["Tag"] = Relationship(back_populates="posts", link_model=PostTagLink)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        return v.lower().replace(' ', '-').replace('_', '-')

class Comment(SQLModel, table=True):
    __table_args__ = (
        Index('idx_comment_post', 'post_id'),
        Index('idx_comment_author', 'author_id'),
        Index('idx_comment_parent', 'parent_id'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    post_id: UUID = Field(foreign_key="post.id")
    author_id: UUID = Field(foreign_key="user.id")
    parent_id: Optional[UUID] = Field(default=None, foreign_key="comment.id")
    content: str
    is_approved: bool = Field(default=True)

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    # Soft delete
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None

    # Relationships
    post: Post = Relationship(back_populates="comments")
    author: User = Relationship(back_populates="comments")

class Tag(SQLModel, table=True):
    __table_args__ = (
        Index('idx_tag_slug', 'slug'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(unique=True, index=True)
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    posts: List[Post] = Relationship(back_populates="tags", link_model=PostTagLink)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        return v.lower().replace(' ', '-').replace('_', '-')
```

## Multi-tenant SaaS

Complete multi-tenant SaaS schema with organizations, workspaces, and users.

```python
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel, Column
from sqlalchemy import Index, DateTime, func
from pydantic import EmailStr, HttpUrl, field_validator

# Enums
class SubscriptionTier(str, Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    TRIAL = "trial"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class MemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    GUEST = "guest"

# Link tables
class OrganizationMember(SQLModel, table=True):
    __table_args__ = (
        Index('idx_org_member_user', 'user_id'),
        Index('idx_org_member_org', 'organization_id'),
    )

    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", primary_key=True)
    role: MemberRole = Field(default=MemberRole.MEMBER)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

class WorkspaceMember(SQLModel, table=True):
    __table_args__ = (
        Index('idx_workspace_member_user', 'user_id'),
        Index('idx_workspace_member_workspace', 'workspace_id'),
    )

    user_id: UUID = Field(foreign_key="user.id", primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id", primary_key=True)
    role: MemberRole = Field(default=MemberRole.MEMBER)
    joined_at: datetime = Field(default_factory=datetime.utcnow)

# Models
class User(SQLModel, table=True):
    __table_args__ = (
        Index('idx_user_email', 'email'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    full_name: str
    avatar_url: Optional[HttpUrl] = None

    # Authentication
    hashed_password: str
    is_active: bool = Field(default=True)
    email_verified: bool = Field(default=False)

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
    last_login: Optional[datetime] = None

    # Soft delete
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None

    # Relationships
    organizations: List["Organization"] = Relationship(
        back_populates="members",
        link_model=OrganizationMember
    )
    workspaces: List["Workspace"] = Relationship(
        back_populates="members",
        link_model=WorkspaceMember
    )

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: str) -> str:
        return v.lower()

class Organization(SQLModel, table=True):
    __table_args__ = (
        Index('idx_org_slug', 'slug'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True)
    slug: str = Field(unique=True, index=True)
    description: Optional[str] = None
    logo_url: Optional[HttpUrl] = None
    website: Optional[HttpUrl] = None

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    # Soft delete
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None

    # Relationships
    members: List[User] = Relationship(
        back_populates="organizations",
        link_model=OrganizationMember
    )
    workspaces: List["Workspace"] = Relationship(back_populates="organization")
    subscription: Optional["Subscription"] = Relationship(back_populates="organization")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        return v.lower().replace(' ', '-').replace('_', '-')

class Workspace(SQLModel, table=True):
    __table_args__ = (
        Index('idx_workspace_org', 'organization_id'),
        Index('idx_workspace_slug', 'organization_id', 'slug', unique=True),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id")
    name: str = Field(index=True)
    slug: str = Field(index=True)
    description: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    # Soft delete
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None

    # Relationships
    organization: Organization = Relationship(back_populates="workspaces")
    members: List[User] = Relationship(
        back_populates="workspaces",
        link_model=WorkspaceMember
    )
    projects: List["Project"] = Relationship(back_populates="workspace")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        return v.lower().replace(' ', '-').replace('_', '-')

class Project(SQLModel, table=True):
    __table_args__ = (
        Index('idx_project_workspace', 'workspace_id'),
        Index('idx_project_slug', 'workspace_id', 'slug', unique=True),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    workspace_id: UUID = Field(foreign_key="workspace.id")
    name: str = Field(index=True)
    slug: str = Field(index=True)
    description: Optional[str] = None

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )

    # Soft delete
    is_deleted: bool = Field(default=False, index=True)
    deleted_at: Optional[datetime] = None

    # Relationship
    workspace: Workspace = Relationship(back_populates="projects")

class Subscription(SQLModel, table=True):
    __table_args__ = (
        Index('idx_subscription_org', 'organization_id'),
        Index('idx_subscription_status', 'status'),
    )

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    organization_id: UUID = Field(foreign_key="organization.id", unique=True)
    tier: SubscriptionTier = Field(default=SubscriptionTier.FREE)
    status: SubscriptionStatus = Field(default=SubscriptionStatus.TRIAL)

    # Billing
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None

    # Limits
    max_workspaces: int = Field(default=1)
    max_members: int = Field(default=5)

    # Timestamps
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
    trial_ends_at: Optional[datetime] = None
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None

    # Relationship
    organization: Organization = Relationship(back_populates="subscription")
```
