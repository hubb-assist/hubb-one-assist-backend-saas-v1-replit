"""
Esquemas Pydantic para validação de dados na API de Insumos (Versão Minimal).
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator

# Esquemas muito simples para teste
class ModuloAssociationBase(BaseModel):
    module_id: UUID
    quantidade_padrao: int = 1
    observacao: Optional[str] = None
    
    model_config = {"from_attributes": True}

class ModuloAssociationCreate(ModuloAssociationBase):
    pass

class ModuloAssociationResponse(ModuloAssociationBase):
    pass

class InsumoBase(BaseModel):
    nome: str
    descricao: str
    valor_unitario: float
    estoque_atual: int = 0

class InsumoCreate(InsumoBase):
    subscriber_id: UUID

class InsumoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    valor_unitario: Optional[float] = None
    estoque_atual: Optional[int] = None

class InsumoResponse(InsumoBase):
    id: UUID
    subscriber_id: UUID
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class InsumoEstoqueMovimento(BaseModel):
    quantidade: int
    tipo_movimento: str = Field(pattern=r'^(entrada|saida)$')
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "quantidade": 10,
                "tipo_movimento": "entrada"
            }
        }
    }

class InsumoFilter(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None