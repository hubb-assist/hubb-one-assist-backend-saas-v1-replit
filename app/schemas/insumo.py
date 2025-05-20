"""
Esquemas Pydantic para validação de dados na API de Insumos.
"""

from datetime import datetime
from typing import List, Optional, ClassVar
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

class ModuloAssociationBase(BaseModel):
    """
    Esquema base para associação entre Insumo e Módulo.
    """
    module_id: UUID
    quantidade_padrao: int = Field(1, ge=1, description="Quantidade padrão do insumo utilizada no módulo")
    observacao: Optional[str] = None
    module_nome: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class ModuloAssociationCreate(ModuloAssociationBase):
    """
    Esquema para criação de associação entre Insumo e Módulo.
    """
    pass


class ModuloAssociationResponse(ModuloAssociationBase):
    """
    Esquema para resposta de associação entre Insumo e Módulo.
    """
    pass


class InsumoBase(BaseModel):
    """
    Esquema base para Insumo com campos comuns.
    """
    nome: str = Field(..., min_length=1, max_length=100, description="Nome do insumo")
    descricao: str = Field(..., min_length=1, description="Descrição detalhada do insumo")
    categoria: str = Field(..., min_length=1, max_length=50, description="Categoria do insumo")
    valor_unitario: float = Field(..., gt=0, description="Valor unitário do insumo")
    unidade_medida: str = Field(..., min_length=1, max_length=20, description="Unidade de medida")
    estoque_minimo: int = Field(..., ge=0, description="Estoque mínimo recomendado")
    estoque_atual: int = Field(..., ge=0, description="Quantidade atual em estoque")
    fornecedor: Optional[str] = Field(None, max_length=100, description="Nome do fornecedor")
    codigo_referencia: Optional[str] = Field(None, max_length=50, description="Código de referência")
    data_validade: Optional[datetime] = Field(None, description="Data de validade")
    data_compra: Optional[datetime] = Field(None, description="Data da última compra")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    modules_used: List[ModuloAssociationCreate] = Field(default_factory=list, description="Módulos associados ao insumo")

    @field_validator('data_validade')
    def data_validade_futuro(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Valida se a data de validade é futura"""
        if v and v < datetime.utcnow():
            raise ValueError("Data de validade deve ser futura")
        return v

    @field_validator('data_compra')
    def data_compra_passado(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Valida se a data de compra é passada"""
        if v and v > datetime.utcnow():
            raise ValueError("Data de compra não pode ser futura")
        return v


class InsumoCreate(InsumoBase):
    """
    Esquema para criação de um novo Insumo.
    """
    subscriber_id: UUID = Field(..., description="ID do assinante (multitenant)")


class InsumoUpdate(BaseModel):
    """
    Esquema para atualização de um Insumo existente.
    
    Todos os campos são opcionais para permitir atualizações parciais.
    """
    nome: Optional[str] = Field(None, min_length=1, max_length=100, description="Nome do insumo")
    descricao: Optional[str] = Field(None, min_length=1, description="Descrição detalhada do insumo")
    categoria: Optional[str] = Field(None, min_length=1, max_length=50, description="Categoria do insumo")
    valor_unitario: Optional[float] = Field(None, gt=0, description="Valor unitário do insumo")
    unidade_medida: Optional[str] = Field(None, min_length=1, max_length=20, description="Unidade de medida")
    estoque_minimo: Optional[int] = Field(None, ge=0, description="Estoque mínimo recomendado")
    estoque_atual: Optional[int] = Field(None, ge=0, description="Quantidade atual em estoque")
    fornecedor: Optional[str] = Field(None, max_length=100, description="Nome do fornecedor")
    codigo_referencia: Optional[str] = Field(None, max_length=50, description="Código de referência")
    data_validade: Optional[datetime] = Field(None, description="Data de validade")
    data_compra: Optional[datetime] = Field(None, description="Data da última compra")
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    modules_used: Optional[List[ModuloAssociationCreate]] = None

    @field_validator('data_validade')
    def data_validade_futuro(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Valida se a data de validade é futura"""
        if v and v < datetime.utcnow():
            raise ValueError("Data de validade deve ser futura")
        return v

    @field_validator('data_compra')
    def data_compra_passado(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Valida se a data de compra é passada"""
        if v and v > datetime.utcnow():
            raise ValueError("Data de compra não pode ser futura")
        return v


class InsumoResponse(BaseModel):
    """
    Esquema para resposta de um Insumo.
    
    Inclui campos somente leitura como ID, datas de criação/atualização
    e status de ativação.
    """
    id: UUID
    nome: str
    descricao: str
    categoria: str
    valor_unitario: float
    unidade_medida: str
    estoque_minimo: int
    estoque_atual: int
    fornecedor: Optional[str] = None
    codigo_referencia: Optional[str] = None
    data_validade: Optional[datetime] = None
    data_compra: Optional[datetime] = None
    observacoes: Optional[str] = None
    modules_used: List[ModuloAssociationResponse] = Field(default_factory=list)
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    abaixo_minimo: bool = Field(
        False, 
        description="Indica se o estoque está abaixo do mínimo"
    )
    expirado: bool = Field(
        False, 
        description="Indica se o insumo está expirado"
    )

    model_config = {
        "from_attributes": True
    }


class InsumoEstoqueMovimento(BaseModel):
    """
    Esquema para movimentação de estoque (entrada ou saída).
    """
    quantidade: int = Field(..., gt=0, description="Quantidade a ser adicionada ou removida")
    tipo_movimento: str = Field(..., pattern=r'^(entrada|saida)$', description="Tipo de movimento: 'entrada' ou 'saida'")

    model_config = {
        "json_schema_extra": {
            "example": {
                "quantidade": 10,
                "tipo_movimento": "entrada"
            }
        }
    }


class InsumoFilter(BaseModel):
    """
    Esquema para filtros na listagem de insumos.
    """
    nome: Optional[str] = Field(None, description="Filtrar por nome (busca parcial)")
    categoria: Optional[str] = Field(None, description="Filtrar por categoria (busca exata)")
    fornecedor: Optional[str] = Field(None, description="Filtrar por fornecedor (busca parcial)")
    estoque_baixo: Optional[bool] = Field(None, description="Filtrar insumos com estoque abaixo do mínimo")
    module_id: Optional[UUID] = Field(None, description="Filtrar por módulo associado")