"""
Schemas Pydantic para usuários
"""

import uuid
from datetime import datetime
from typing import Optional, List, Union

from pydantic import BaseModel, EmailStr, Field, ConfigDict

from app.db.models import UserRole

# Schemas Base para Usuário
class UserBase(BaseModel):
    """Schema base para usuários com atributos comuns"""
    nome: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    is_active: Optional[bool] = True
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

# Schema para criação de usuário
class UserCreate(UserBase):
    """Schema para criação de novo usuário"""
    senha: str = Field(..., min_length=8, description="Senha deve ter pelo menos 8 caracteres")
    role: Optional[UserRole] = UserRole.COLABORADOR_NIVEL_2

# Schema para atualização de usuário
class UserUpdate(BaseModel):
    """Schema para atualização de usuário - todos os campos são opcionais"""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    senha: Optional[str] = Field(None, min_length=8)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid"  # impede campos extras
    )

# Schema para resposta de usuário
class UserResponse(UserBase):
    """Schema para resposta de usuário - inclui campos somente leitura"""
    id: uuid.UUID
    role: UserRole
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