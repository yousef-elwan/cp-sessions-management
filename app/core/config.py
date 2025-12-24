"""Application Configuration

This module defines application settings using Pydantic Settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

#basesettings bring the values from .env
class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    All settings are loaded from the .env file in the project root.
    """
    
    
    # Database Configuration
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL database connection URL"
    )
    
    # Security Configuration
    SECRET_KEY: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT token signing (min 32 characters)"
    )
    ALGORITHM: str = Field(
        default="HS256",
        description="JWT encoding algorithm"
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        ge=1,
        le=43200,  # Max 30 days
        description="JWT token expiration time in minutes"
    )
    
    # Super Admin Configuration
    SUPER_ADMIN_EMAIL: str = Field(
        default="superadmin@example.com",
        description="Default Super Admin email"
    )
    SUPER_ADMIN_PASSWORD: str = Field(
        default="SuperAdmin123!",
        description="Default Super Admin password"
    )
    
    # CORS Configuration
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="Comma-separated list of allowed CORS origins"
    )
    
    # Application Configuration
    DEBUG: bool = Field(
        default=False,
        description="Debug mode flag"
    )
    
    @field_validator('DATABASE_URL')
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v.startswith(('postgresql+asyncpg://', 'postgresql://')):
            raise ValueError('DATABASE_URL must start with postgresql+asyncpg:// or postgresql://')
        return v
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key strength."""
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v

    #This piece of code is configuring how Pydantic BaseSettings should load and handle environment variables
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Global settings instance
settings = Settings()
