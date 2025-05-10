"""
Schemas Pydantic para módulos funcionais
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class ModuleBase(BaseModel):
    """Schema base para módulos com atributos comuns"""
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: Optional[str] = None
    is_active: Optional[bool] = True

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class ModuleCreate(ModuleBase):
    """Schema para criação de novo módulo"""
    pass


class ModuleUpdate(BaseModel):
    """Schema para atualização de módulo - todos os campos são opcionais"""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid"  # impede campos extras
    )


class ModuleResponse(ModuleBase):
    """Schema para resposta de módulo - inclui campos somente leitura"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class PaginatedModuleResponse(BaseModel):
    """Schema para resposta paginada de módulos"""
    total: int
    page: int
    size: int
    items: List[ModuleResponse]