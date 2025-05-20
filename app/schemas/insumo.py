"""
Esquemas de validação para Insumos usando Pydantic.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator


class InsumoBase(BaseModel):
    """Esquema base para Insumo."""
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do insumo")
    descricao: str = Field(..., min_length=1, max_length=500, description="Descrição detalhada do insumo")
    categoria: str = Field(..., description="Categoria do insumo (ex: MEDICAMENTO, EQUIPAMENTO, MATERIAL)")
    valor_unitario: Decimal = Field(..., ge=0, description="Valor unitário do insumo")
    unidade_medida: str = Field(..., min_length=1, max_length=10, description="Unidade de medida (UN, CX, ML, KG)")
    estoque_minimo: int = Field(..., ge=0, description="Quantidade mínima recomendada em estoque")
    estoque_atual: int = Field(..., ge=0, description="Quantidade atual em estoque")
    fornecedor: Optional[str] = Field(None, max_length=100, description="Nome do fornecedor")
    codigo_referencia: Optional[str] = Field(None, max_length=50, description="Código de referência ou SKU")
    data_validade: Optional[datetime] = Field(None, description="Data de validade do insumo")
    data_compra: Optional[datetime] = Field(None, description="Data da última compra")
    observacoes: Optional[str] = Field(None, max_length=1000, description="Observações adicionais")
    modules_used: Optional[List[UUID]] = Field(None, description="IDs dos módulos onde este insumo é usado")

    @validator('categoria')
    def validate_categoria(cls, v):
        """Valida se a categoria é permitida."""
        categorias_validas = ['MEDICAMENTO', 'EQUIPAMENTO', 'MATERIAL', 'INSUMO_MEDICO', 'OUTROS']
        if v.upper() not in categorias_validas:
            raise ValueError(f"Categoria deve ser uma das seguintes: {', '.join(categorias_validas)}")
        return v.upper()
    
    @validator('unidade_medida')
    def validate_unidade_medida(cls, v):
        """Valida se a unidade de medida é permitida."""
        unidades_validas = ['UN', 'CX', 'ML', 'MG', 'G', 'KG', 'L', 'PCT', 'DOSE']
        if v.upper() not in unidades_validas:
            raise ValueError(f"Unidade de medida deve ser uma das seguintes: {', '.join(unidades_validas)}")
        return v.upper()


class InsumoCreate(InsumoBase):
    """Esquema para criação de um novo Insumo."""
    subscriber_id: UUID = Field(..., description="ID do assinante ao qual o insumo pertence")


class InsumoUpdate(BaseModel):
    """Esquema para atualização de um Insumo existente."""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = Field(None, min_length=1, max_length=500)
    categoria: Optional[str] = Field(None)
    valor_unitario: Optional[Decimal] = Field(None, ge=0)
    unidade_medida: Optional[str] = Field(None, min_length=1, max_length=10)
    estoque_minimo: Optional[int] = Field(None, ge=0)
    estoque_atual: Optional[int] = Field(None, ge=0)
    fornecedor: Optional[str] = Field(None, max_length=100)
    codigo_referencia: Optional[str] = Field(None, max_length=50)
    data_validade: Optional[datetime] = Field(None)
    data_compra: Optional[datetime] = Field(None)
    observacoes: Optional[str] = Field(None, max_length=1000)
    modules_used: Optional[List[UUID]] = Field(None)
    is_active: Optional[bool] = Field(None)

    @validator('categoria')
    def validate_categoria(cls, v):
        """Valida se a categoria é permitida."""
        if v is None:
            return v
        categorias_validas = ['MEDICAMENTO', 'EQUIPAMENTO', 'MATERIAL', 'INSUMO_MEDICO', 'OUTROS']
        if v.upper() not in categorias_validas:
            raise ValueError(f"Categoria deve ser uma das seguintes: {', '.join(categorias_validas)}")
        return v.upper()
    
    @validator('unidade_medida')
    def validate_unidade_medida(cls, v):
        """Valida se a unidade de medida é permitida."""
        if v is None:
            return v
        unidades_validas = ['UN', 'CX', 'ML', 'MG', 'G', 'KG', 'L', 'PCT', 'DOSE']
        if v.upper() not in unidades_validas:
            raise ValueError(f"Unidade de medida deve ser uma das seguintes: {', '.join(unidades_validas)}")
        return v.upper()


class InsumoInDB(InsumoBase):
    """Esquema para Insumo já persistido no banco de dados."""
    id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class InsumoResponse(InsumoInDB):
    """Esquema para resposta da API sobre Insumos."""
    estoque_baixo: bool = Field(..., description="Indica se o estoque está abaixo do mínimo")
    valor_total_estoque: Decimal = Field(..., description="Valor total do insumo em estoque")

    class Config:
        orm_mode = True


class InsumoListResponse(BaseModel):
    """Esquema para resposta de listagem de Insumos com paginação."""
    items: List[InsumoResponse]
    total: int
    skip: int
    limit: int