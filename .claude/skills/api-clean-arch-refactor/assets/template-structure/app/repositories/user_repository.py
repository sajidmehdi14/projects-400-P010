"""
User repository - Database operations for users
"""
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import UserDB
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserDB]):
    """Repository for user database operations"""

    def __init__(self, db: Session):
        super().__init__(UserDB, db)

    def get_by_email(self, email: str) -> Optional[UserDB]:
        """Get user by email"""
        return self.db.query(UserDB).filter(UserDB.email == email).first()

    def get_by_username(self, username: str) -> Optional[UserDB]:
        """Get user by username"""
        return self.db.query(UserDB).filter(UserDB.username == username).first()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> list[UserDB]:
        """Get all active users"""
        return (
            self.db.query(UserDB)
            .filter(UserDB.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def email_exists(self, email: str) -> bool:
        """Check if email is already registered"""
        return self.db.query(UserDB).filter(UserDB.email == email).first() is not None

    def username_exists(self, username: str) -> bool:
        """Check if username is already taken"""
        return self.db.query(UserDB).filter(UserDB.username == username).first() is not None
