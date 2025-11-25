from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID

class UserCreate(BaseModel):
    name: str = Field(..., max_length=150)
    email: EmailStr = Field(..., max_length=150)
    password: str = Field(..., min_length=8)
    role: Optional[str] = "student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserInDB(BaseModel):
    id: UUID
    name: str
    email: str
    role: str
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True
