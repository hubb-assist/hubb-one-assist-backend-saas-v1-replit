"""
Schemas para validação e serialização de dados de insumos.
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, validator


class InsumoBase(BaseModel):
    """Atributos comuns para criação e leitura de insumos."""
    nome: str = Field(..., min_length=2, max_length=100, description="Nome do insumo")
    tipo: str = Field(..., min_length=2, max_length=50, description="Tipo do insumo (ex: medicamento, material)")
    unidade: str = Field(..., min_length=1, max_length=30, description="Unidade de medida (ex: unidade, caixa, ml)")
    categoria: str = Field(..., min_length=2, max_length=50, description="Categoria do insumo (ex: cirúrgico)")
    quantidade: float = Field(0.0, ge=0, description="Quantidade disponível do insumo")
    observacoes: Optional[str] = Field(None, max_length=500, description="Observações adicionais sobre o insumo")
    modulo_id: Optional[UUID] = Field(None, description="ID do módulo ao qual o insumo está relacionado")
    
    @validator("nome", "tipo", "unidade", "categoria")
    def validate_text_fields(cls, v, values, **kwargs):
        if v and not v.strip():
            field_name = kwargs.get("field_name", "campo")
            raise ValueError(f"O {field_name} não pode conter apenas espaços")
        return v.strip() if v else v


class InsumoCreate(InsumoBase):
    """Schema para criação de insumo."""
    pass


class InsumoUpdate(BaseModel):
    """Schema para atualização parcial de insumo."""
    nome: Optional[str] = Field(None, min_length=2, max_length=100, description="Nome do insumo")
    tipo: Optional[str] = Field(None, min_length=2, max_length=50, description="Tipo do insumo")
    unidade: Optional[str] = Field(None, min_length=1, max_length=30, description="Unidade de medida")
    categoria: Optional[str] = Field(None, min_length=2, max_length=50, description="Categoria do insumo")
    quantidade: Optional[float] = Field(None, ge=0, description="Quantidade disponível")
    observacoes: Optional[str] = Field(None, max_length=500, description="Observações adicionais")
    modulo_id: Optional[UUID] = Field(None, description="ID do módulo relacionado")
    is_active: Optional[bool] = Field(None, description="Indica se o insumo está ativo")
    
    @validator("nome", "tipo", "unidade", "categoria")
    def validate_text_fields(cls, v, values, **kwargs):
        if v and not v.strip():
            field_name = kwargs.get("field_name", "campo")
            raise ValueError(f"O {field_name} não pode conter apenas espaços")
        return v.strip() if v else v


class InsumoResponse(InsumoBase):
    """Schema para resposta de insumo."""
    id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class InsumoListResponse(BaseModel):
    """Schema para resposta de listagem de insumos."""
    items: List[InsumoResponse]
    total: int
    skip: int
    limit: int
    filters: dict
    
    class Config:
        orm_mode = True