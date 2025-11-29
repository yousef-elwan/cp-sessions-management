"""Password Hashing Utilities

This module provides password hashing and verification using Argon2.
"""
from passlib.context import CryptContext


# Use Argon2 for password hashing (modern, secure)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a password using Argon2.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
        
    Example:
        >>> hashed = get_password_hash("MySecurePassword123!")
        >>> print(hashed)
        $argon2id$v=19$m=65536,t=3,p=4$...
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        >>> hashed = get_password_hash("password123")
        >>> verify_password("password123", hashed)
        True
        >>> verify_password("wrongpass", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)