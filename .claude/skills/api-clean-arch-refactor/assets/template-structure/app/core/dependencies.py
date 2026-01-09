"""
Dependency injection for FastAPI
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.item_repository import ItemRepository
from app.services.user_service import UserService
from app.services.item_service import ItemService


# Database dependency
DatabaseDep = Annotated[Session, Depends(get_db)]


# Repository dependencies
def get_user_repository(db: DatabaseDep) -> UserRepository:
    """Get user repository instance"""
    return UserRepository(db)


def get_item_repository(db: DatabaseDep) -> ItemRepository:
    """Get item repository instance"""
    return ItemRepository(db)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
ItemRepositoryDep = Annotated[ItemRepository, Depends(get_item_repository)]


# Service dependencies
def get_user_service(repository: UserRepositoryDep) -> UserService:
    """Get user service instance"""
    return UserService(repository)


def get_item_service(repository: ItemRepositoryDep) -> ItemService:
    """Get item service instance"""
    return ItemService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]
