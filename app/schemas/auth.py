"""
Schemas Pydantic para autenticação
"""

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class LoginRequest(BaseModel):
    """Schema para requisição de login"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "usuario@exemplo.com",
                "password": "senha123"
            }
        }
    )


class Token(BaseModel):
    """Schema para resposta com tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    
class TokenData(BaseModel):
    """Schema para dados extraídos do token"""
    user_id: int
    email: Optional[str] = None
    role: Optional[str] = None
    subscriber_id: Optional[str] = None
    segment_id: Optional[str] = None
    permissions: Optional[list] = None
    exp: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    """Schema para requisição de refresh token"""
    refresh_token: str