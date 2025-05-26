"""
Schemas Pydantic para segmentos
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SegmentBase(BaseModel):
    """Schema base para segmentos com atributos comuns"""
    nome: str = Field(..., min_length=2, max_length=100)
    descricao: Optional[str] = None
    is_active: Optional[bool] = True

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class SegmentCreate(SegmentBase):
    """Schema para criação de novo segmento"""
    pass


class SegmentUpdate(BaseModel):
    """Schema para atualização de segmento - todos os campos são opcionais"""
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = None
    is_active: Optional[bool] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid"  # impede campos extras
    )


class SegmentResponse(SegmentBase):
    """Schema para resposta de segmento - inclui campos somente leitura"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class PaginatedSegmentResponse(BaseModel):
    """Schema para resposta paginada de segmentos"""
    total: int
    page: int
    size: int
    items: List[SegmentResponse]