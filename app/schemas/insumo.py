"""
Esquemas Pydantic para Insumos.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InsumoBase(BaseModel):
    """Esquema base para Insumo"""
    nome: str = Field(..., description="Nome do insumo")
    tipo: str = Field(..., description="Tipo do insumo (medicamento, material, equipamento)")
    unidade: str = Field(..., description="Unidade de medida (ampola, caixa, unidade)")
    categoria: str = Field(..., description="Categoria do insumo")
    quantidade: float = Field(0, description="Quantidade disponível", ge=0)
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    modulo_id: Optional[UUID] = Field(None, description="ID do módulo ao qual o insumo pertence")


class InsumoCreate(InsumoBase):
    """Esquema para criação de Insumo"""
    pass


class InsumoUpdate(BaseModel):
    """Esquema para atualização de Insumo"""
    nome: Optional[str] = Field(None, description="Nome do insumo")
    tipo: Optional[str] = Field(None, description="Tipo do insumo (medicamento, material, equipamento)")
    unidade: Optional[str] = Field(None, description="Unidade de medida (ampola, caixa, unidade)")
    categoria: Optional[str] = Field(None, description="Categoria do insumo")
    quantidade: Optional[float] = Field(None, description="Quantidade disponível", ge=0)
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    modulo_id: Optional[UUID] = Field(None, description="ID do módulo ao qual o insumo pertence")


class InsumoResponse(InsumoBase):
    """Esquema para resposta de Insumo"""
    id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InsumoList(BaseModel):
    """Esquema para lista de Insumos"""
    total: int
    items: List[InsumoResponse]
    
    class Config:
        from_attributes = True