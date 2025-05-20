"""
Schemas Pydantic para o módulo de Insumos.
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class InsumoBase(BaseModel):
    """
    Atributos base para um insumo.
    """
    nome: str = Field(..., description="Nome do insumo", min_length=3, max_length=100)
    tipo: str = Field(..., description="Tipo do insumo (ex: medicamento, equipamento)", min_length=3, max_length=50)
    unidade: str = Field(..., description="Unidade de medida (ex: kg, litro, unidade)", min_length=1, max_length=30)
    categoria: str = Field(..., description="Categoria do insumo", min_length=3, max_length=50)
    quantidade: float = Field(..., description="Quantidade disponível", ge=0)
    observacoes: Optional[str] = Field(None, description="Observações sobre o insumo", max_length=500)
    modulo_id: Optional[UUID] = Field(None, description="ID do módulo relacionado")
    is_active: bool = Field(True, description="Se o insumo está ativo")


class InsumoCreate(InsumoBase):
    """
    Atributos para criar um novo insumo.
    """
    pass


class InsumoUpdate(BaseModel):
    """
    Atributos que podem ser atualizados em um insumo.
    """
    nome: Optional[str] = Field(None, description="Nome do insumo", min_length=3, max_length=100)
    tipo: Optional[str] = Field(None, description="Tipo do insumo (ex: medicamento, equipamento)", min_length=3, max_length=50)
    unidade: Optional[str] = Field(None, description="Unidade de medida (ex: kg, litro, unidade)", min_length=1, max_length=30)
    categoria: Optional[str] = Field(None, description="Categoria do insumo", min_length=3, max_length=50)
    quantidade: Optional[float] = Field(None, description="Quantidade disponível", ge=0)
    observacoes: Optional[str] = Field(None, description="Observações sobre o insumo", max_length=500)
    modulo_id: Optional[UUID] = Field(None, description="ID do módulo relacionado")
    is_active: Optional[bool] = Field(None, description="Se o insumo está ativo")
    
    class Config:
        schema_extra = {
            "example": {
                "nome": "Seringa descartável",
                "tipo": "Equipamento",
                "unidade": "unidade",
                "categoria": "Material descartável",
                "quantidade": 100.0,
                "observacoes": "Utilizar conforme protocolo",
                "is_active": True
            }
        }


class InsumoInDB(InsumoBase):
    """
    Atributos de um insumo como armazenado no banco de dados.
    """
    id: UUID
    subscriber_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class InsumoResponse(InsumoInDB):
    """
    Resposta para as operações de insumo.
    """
    pass


class InsumoItem(InsumoInDB):
    """
    Insumo em uma listagem.
    """
    pass


class InsumoList(BaseModel):
    """
    Lista paginada de insumos.
    """
    total: int
    items: List[InsumoItem]