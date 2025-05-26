"""
Esquemas Pydantic para validação de dados na API de Movimentações de Insumos.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class InsumoMovimentacaoBase(BaseModel):
    """
    Esquema base para Movimentação de Estoque com campos comuns.
    """
    quantidade: int = Field(..., gt=0, description="Quantidade movimentada (sempre positiva)")
    tipo_movimento: str = Field(..., pattern=r'^(entrada|saida)$', description="Tipo de movimento: 'entrada' ou 'saida'")
    motivo: Optional[str] = Field(None, max_length=255, description="Motivo da movimentação")
    observacao: Optional[str] = Field(None, description="Observações adicionais")


class InsumoMovimentacaoCreate(InsumoMovimentacaoBase):
    """
    Esquema para criação de uma nova Movimentação de Estoque.
    """
    insumo_id: UUID = Field(..., description="ID do insumo")
    
    @field_validator('quantidade')
    def quantidade_positiva(cls, v: int) -> int:
        """Valida se a quantidade é positiva"""
        if v <= 0:
            raise ValueError("Quantidade deve ser maior que zero")
        return v


class InsumoMovimentacaoUpdate(BaseModel):
    """
    Esquema para atualização de uma Movimentação existente.
    
    Permitimos apenas atualizar o motivo e observações, já que
    a quantidade e tipo não devem ser alterados após o registro.
    """
    motivo: Optional[str] = Field(None, max_length=255, description="Motivo da movimentação")
    observacao: Optional[str] = Field(None, description="Observações adicionais")


class InsumoMovimentacaoResponse(BaseModel):
    """
    Esquema para resposta de uma Movimentação de Estoque.
    
    Inclui campos somente leitura como ID, timestamps e dados do insumo.
    """
    id: UUID
    insumo_id: UUID
    quantidade: int
    tipo_movimento: str
    motivo: Optional[str] = None
    estoque_anterior: int
    estoque_resultante: int
    observacao: Optional[str] = None
    usuario_id: Optional[UUID] = None
    subscriber_id: UUID
    created_at: datetime
    
    # Campos opcionais com informações do insumo (para listagens enriquecidas)
    insumo_nome: Optional[str] = None
    insumo_categoria: Optional[str] = None
    insumo_unidade_medida: Optional[str] = None
    usuario_nome: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class InsumoEstoqueHistoricoRequest(BaseModel):
    """
    Esquema para filtragem do histórico de movimentações.
    """
    insumo_id: Optional[UUID] = Field(None, description="Filtrar por ID do insumo")
    tipo_movimento: Optional[str] = Field(None, pattern=r'^(entrada|saida)$', description="Filtrar por tipo de movimento")
    data_inicio: Optional[datetime] = Field(None, description="Data inicial para filtro")
    data_fim: Optional[datetime] = Field(None, description="Data final para filtro")
    
    @field_validator('data_fim')
    def data_fim_maior_que_inicio(cls, v: Optional[datetime], values) -> Optional[datetime]:
        """Valida se a data final é posterior à data inicial, se ambas forem fornecidas"""
        if v and 'data_inicio' in values and values['data_inicio'] and v < values['data_inicio']:
            raise ValueError("Data final deve ser posterior à data inicial")
        return v