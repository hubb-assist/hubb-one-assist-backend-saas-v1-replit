"""
Esquemas Pydantic para validação de insumos na API.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator


class InsumoModuleAssociationBase(BaseModel):
    """Esquema base para associação entre insumo e módulo"""
    module_id: UUID
    quantidade_padrao: int = Field(1, description="Quantidade padrão utilizada deste insumo pelo módulo")
    observacao: Optional[str] = Field(None, description="Observação sobre o uso deste insumo no módulo")


class InsumoModuleAssociationCreate(InsumoModuleAssociationBase):
    """Esquema para criação de associação entre insumo e módulo"""
    pass


class InsumoModuleAssociationResponse(InsumoModuleAssociationBase):
    """Esquema para resposta de associação entre insumo e módulo"""
    module_nome: Optional[str] = Field(None, description="Nome do módulo (preenchido automaticamente)")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InsumoBase(BaseModel):
    """Esquema base para insumos"""
    nome: str = Field(..., min_length=2, max_length=150, description="Nome do insumo")
    descricao: Optional[str] = Field(None, description="Descrição detalhada do insumo")
    categoria: str = Field(..., min_length=2, max_length=100, description="Categoria do insumo (ex: Material de Escritório, Produtos de Limpeza)")
    valor_unitario: float = Field(..., gt=0, description="Valor unitário do insumo")
    unidade_medida: str = Field(..., min_length=1, max_length=50, description="Unidade de medida (ex: Unidade, Kg, Litro)")
    estoque_minimo: int = Field(1, ge=0, description="Estoque mínimo recomendado")
    estoque_atual: int = Field(0, ge=0, description="Estoque atual")
    fornecedor: Optional[str] = Field(None, description="Nome do fornecedor")
    codigo_referencia: Optional[str] = Field(None, description="Código de referência do fornecedor ou interno")
    data_validade: Optional[datetime] = Field(None, description="Data de validade")
    data_compra: Optional[datetime] = Field(None, description="Data da última compra")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")


class InsumoCreate(InsumoBase):
    """Esquema para criação de insumo"""
    subscriber_id: UUID = Field(..., description="ID do assinante que possui o insumo")
    modules_used: Optional[List[InsumoModuleAssociationCreate]] = Field([], description="Módulos onde este insumo é utilizado")


class InsumoUpdate(BaseModel):
    """Esquema para atualização de insumo (todos os campos são opcionais)"""
    nome: Optional[str] = Field(None, min_length=2, max_length=150, description="Nome do insumo")
    descricao: Optional[str] = Field(None, description="Descrição detalhada do insumo")
    categoria: Optional[str] = Field(None, min_length=2, max_length=100, description="Categoria do insumo (ex: Material de Escritório, Produtos de Limpeza)")
    valor_unitario: Optional[float] = Field(None, gt=0, description="Valor unitário do insumo")
    unidade_medida: Optional[str] = Field(None, min_length=1, max_length=50, description="Unidade de medida (ex: Unidade, Kg, Litro)")
    estoque_minimo: Optional[int] = Field(None, ge=0, description="Estoque mínimo recomendado")
    estoque_atual: Optional[int] = Field(None, ge=0, description="Estoque atual")
    fornecedor: Optional[str] = Field(None, description="Nome do fornecedor")
    codigo_referencia: Optional[str] = Field(None, description="Código de referência do fornecedor ou interno")
    data_validade: Optional[datetime] = Field(None, description="Data de validade")
    data_compra: Optional[datetime] = Field(None, description="Data da última compra")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    is_active: Optional[bool] = Field(None, description="Status ativo/inativo do insumo")
    modules_used: Optional[List[InsumoModuleAssociationCreate]] = Field(None, description="Módulos onde este insumo é utilizado")


class InsumoResponse(InsumoBase):
    """Esquema para resposta de insumo"""
    id: UUID
    subscriber_id: UUID
    modules_used: List[InsumoModuleAssociationResponse] = []
    is_active: bool
    created_at: datetime
    updated_at: datetime
    estoque_baixo: bool = Field(False, description="Indica se o estoque está abaixo do mínimo")
    valor_total_estoque: float = Field(0.0, description="Valor total do estoque (estoque_atual * valor_unitario)")

    class Config:
        from_attributes = True


class InsumoListResponse(BaseModel):
    """Esquema para resposta de listagem paginada de insumos"""
    items: List[InsumoResponse]
    total: int
    skip: int
    limit: int

    class Config:
        from_attributes = True