"""
Application configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""

    PROJECT_NAME: str = "FastAPI Clean Architecture"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI application following clean architecture principles"

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
