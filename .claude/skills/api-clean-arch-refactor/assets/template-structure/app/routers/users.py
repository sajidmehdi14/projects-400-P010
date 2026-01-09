"""
User router - API endpoints for users
"""
from fastapi import APIRouter, status

from app.core.dependencies import UserServiceDep
from app.models.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
def get_users(
    service: UserServiceDep,
    skip: int = 0,
    limit: int = 100,
):
    """Get all users"""
    return service.get_users(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, service: UserServiceDep):
    """Get user by ID"""
    return service.get_user(user_id)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, service: UserServiceDep):
    """Create a new user"""
    return service.create_user(user)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, service: UserServiceDep):
    """Update user"""
    return service.update_user(user_id, user)


@router.delete("/{user_id}")
def delete_user(user_id: int, service: UserServiceDep):
    """Delete user"""
    return service.delete_user(user_id)
