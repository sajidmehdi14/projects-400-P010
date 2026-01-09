"""
User service - Business logic for user operations
"""
from typing import Optional
from passlib.context import CryptContext
from fastapi import HTTPException, status

from app.models.user import UserDB, UserCreate, UserUpdate, UserResponse
from app.repositories.user_repository import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user business logic"""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user(self, user_id: int) -> UserResponse:
        """Get user by ID"""
        user = self.repository.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return UserResponse.model_validate(user)

    def get_users(self, skip: int = 0, limit: int = 100) -> list[UserResponse]:
        """Get all users"""
        users = self.repository.get_all(skip=skip, limit=limit)
        return [UserResponse.model_validate(user) for user in users]

    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user"""
        # Check if email already exists
        if self.repository.email_exists(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Check if username already exists
        if self.repository.username_exists(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

        # Hash password
        hashed_password = pwd_context.hash(user_data.password)

        # Create user
        user = UserDB(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
        )

        created_user = self.repository.create(user)
        return UserResponse.model_validate(created_user)

    def update_user(self, user_id: int, user_data: UserUpdate) -> UserResponse:
        """Update user"""
        user = self.repository.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        # Update fields if provided
        if user_data.email is not None:
            if self.repository.email_exists(user_data.email) and user.email != user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered",
                )
            user.email = user_data.email

        if user_data.username is not None:
            if self.repository.username_exists(user_data.username) and user.username != user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken",
                )
            user.username = user_data.username

        if user_data.password is not None:
            user.hashed_password = pwd_context.hash(user_data.password)

        if user_data.is_active is not None:
            user.is_active = user_data.is_active

        updated_user = self.repository.update(user)
        return UserResponse.model_validate(updated_user)

    def delete_user(self, user_id: int) -> dict:
        """Delete user"""
        if not self.repository.exists(user_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        self.repository.delete(user_id)
        return {"message": "User deleted successfully"}

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, username: str, password: str) -> Optional[UserDB]:
        """Authenticate user by username and password"""
        user = self.repository.get_by_username(username)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user
