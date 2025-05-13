"""
Schemas Pydantic para usuários
"""

from datetime import datetime
from typing import Optional, List, Union

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.db.models import UserRole

# Schemas Base para Usuário
class UserBase(BaseModel):
    """Schema base para usuários com atributos comuns"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    is_active: Optional[bool] = True
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Schema para criação de usuário
class UserCreate(UserBase):
    """Schema para criação de novo usuário"""
    password: str = Field(..., min_length=8, description="Senha deve ter pelo menos 8 caracteres")
    role: Optional[UserRole] = UserRole.COLABORADOR_NIVEL_2
    subscriber_id: Optional[str] = None  # ID do assinante associado, opcional para administradores

# Schema para atualização de usuário
class UserUpdate(BaseModel):
    """Schema para atualização de usuário - todos os campos são opcionais"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    subscriber_id: Optional[str] = None  # ID do assinante associado, opcional para administradores
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid"  # impede campos extras
    )

# Schema para resposta de usuário
class UserResponse(UserBase):
    """Schema para resposta de usuário - inclui campos somente leitura"""
    id: int
    role: UserRole
    subscriber_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Schema para lista paginada de usuários
class PaginatedUserResponse(BaseModel):
    """Schema para resposta paginada de usuários"""
    total: int
    page: int
    size: int
    items: List[UserResponse]