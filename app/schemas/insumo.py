"""
Esquemas Pydantic para insumos.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class InsumoModuleAssociationBase(BaseModel):
    """Esquema base para associação entre insumo e módulo."""
    module_id: UUID
    quantidade_padrao: int = Field(default=1, gt=0)
    observacao: Optional[str] = None


class InsumoModuleAssociationCreate(InsumoModuleAssociationBase):
    """Esquema para criação de associação entre insumo e módulo."""
    pass


class InsumoModuleAssociationRead(InsumoModuleAssociationBase):
    """Esquema para leitura de associação entre insumo e módulo."""
    module_nome: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class InsumoBase(BaseModel):
    """Esquema base para insumo."""
    nome: str
    descricao: str
    categoria: str
    valor_unitario: float
    unidade_medida: str
    estoque_minimo: int = Field(default=0, ge=0)
    estoque_atual: int = Field(default=0, ge=0)
    fornecedor: Optional[str] = None
    codigo_referencia: Optional[str] = None
    data_validade: Optional[str] = None
    data_compra: Optional[str] = None
    observacoes: Optional[str] = None


class InsumoCreate(InsumoBase):
    """Esquema para criação de insumo."""
    subscriber_id: Optional[UUID] = None  # Será preenchido a partir do token JWT
    modules_used: Optional[List[InsumoModuleAssociationCreate]] = None

    @validator('valor_unitario')
    def valor_unitario_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Valor unitário deve ser maior que zero')
        return v

    @validator('estoque_minimo')
    def estoque_minimo_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Estoque mínimo não pode ser negativo')
        return v

    @validator('estoque_atual')
    def estoque_atual_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('Estoque atual não pode ser negativo')
        return v


class InsumoUpdate(BaseModel):
    """Esquema para atualização de insumo."""
    nome: Optional[str] = None
    descricao: Optional[str] = None
    categoria: Optional[str] = None
    valor_unitario: Optional[float] = None
    unidade_medida: Optional[str] = None
    estoque_minimo: Optional[int] = None
    estoque_atual: Optional[int] = None
    fornecedor: Optional[str] = None
    codigo_referencia: Optional[str] = None
    data_validade: Optional[str] = None
    data_compra: Optional[str] = None
    observacoes: Optional[str] = None
    modules_used: Optional[List[InsumoModuleAssociationCreate]] = None

    @validator('valor_unitario')
    def valor_unitario_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Valor unitário deve ser maior que zero')
        return v

    @validator('estoque_minimo')
    def estoque_minimo_must_be_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Estoque mínimo não pode ser negativo')
        return v

    @validator('estoque_atual')
    def estoque_atual_must_be_non_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError('Estoque atual não pode ser negativo')
        return v


class InsumoRead(InsumoBase):
    """Esquema para leitura de insumo."""
    id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    modules_used: List[InsumoModuleAssociationRead] = []
    
    class Config:
        orm_mode = True


class EstoqueUpdate(BaseModel):
    """Esquema para atualização de estoque de insumo."""
    quantidade: int = Field(..., gt=0)
    tipo_movimento: str = Field(..., regex='^(entrada|saida)$')
    observacao: Optional[str] = None


class InsumoFilter(BaseModel):
    """Esquema para filtros de busca de insumos."""
    nome: Optional[str] = None
    categoria: Optional[str] = None
    fornecedor: Optional[str] = None
    estoque_baixo: Optional[bool] = None
    module_id: Optional[UUID] = None