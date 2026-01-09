"""
Item models - Database and API schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


# Database Model
class ItemDB(Base):
    """Item database model"""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("UserDB", backref="items")


# Pydantic Schemas (API Models)
class ItemBase(BaseModel):
    """Base item schema"""

    title: str
    description: Optional[str] = None
    price: float


class ItemCreate(ItemBase):
    """Schema for creating an item"""

    pass


class ItemUpdate(BaseModel):
    """Schema for updating an item"""

    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None


class ItemResponse(ItemBase):
    """Schema for item response"""

    id: int
    is_available: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
