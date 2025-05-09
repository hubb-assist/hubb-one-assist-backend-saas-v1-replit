from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.db.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common attributes"""
    name: str
    email: EmailStr
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: Optional[UserRole] = UserRole.COLABORADOR_NIVEL_2


class UserUpdate(BaseModel):
    """Schema for updating a user - all fields are optional"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(extra="forbid")


class UserOut(UserBase):
    """Schema for user responses - includes read-only fields"""
    id: int
    role: UserRole
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """Schema for authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data"""
    user_id: int
    token_type: str
