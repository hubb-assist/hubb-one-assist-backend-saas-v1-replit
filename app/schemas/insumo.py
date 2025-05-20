"""
Schemas Pydantic para validação de Insumos.
"""
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, condecimal, constr
from datetime import datetime

class InsumoBase(BaseModel):
    """Schema base para Insumos."""
    nome: str
    tipo: str
    unidade: str
    valor: condecimal(gt=0, decimal_places=2)
    observacoes: Optional[str] = None
    categoria: constr(strip_whitespace=True, min_length=1)
    modulos: List[constr(strip_whitespace=True, min_length=1)]

class InsumoCreate(InsumoBase):
    """Schema para criação de Insumos."""
    pass

class InsumoUpdate(BaseModel):
    """Schema para atualização de Insumos."""
    nome: Optional[str] = None
    tipo: Optional[str] = None
    unidade: Optional[str] = None
    valor: Optional[condecimal(gt=0, decimal_places=2)] = None
    observacoes: Optional[str] = None
    categoria: Optional[constr(strip_whitespace=True, min_length=1)] = None
    modulos: Optional[List[constr(strip_whitespace=True, min_length=1)]] = None

class InsumoResponse(InsumoBase):
    """Schema para resposta de Insumos."""
    id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True