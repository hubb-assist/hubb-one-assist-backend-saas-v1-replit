from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

class CustoFixoBase(BaseModel):
    """Esquema base para custos fixos."""
    nome: str = Field(..., min_length=1, max_length=255)
    valor: Decimal = Field(..., gt=0)
    data: date
    observacoes: Optional[str] = None
    
    @field_validator('valor')
    @classmethod
    def validate_valor(cls, v: Decimal) -> Decimal:
        """Valida que o valor tenha no máximo 2 casas decimais."""
        if v.quantize(Decimal('0.01')) != v:
            raise ValueError('O valor deve ter no máximo 2 casas decimais')
        return v

class CustoFixoCreate(CustoFixoBase):
    """Esquema para criação de custos fixos."""
    pass

class CustoFixoUpdate(BaseModel):
    """Esquema para atualização de custos fixos."""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    valor: Optional[Decimal] = Field(None, gt=0)
    data: Optional[date] = None
    observacoes: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('valor')
    @classmethod
    def validate_valor(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Valida que o valor tenha no máximo 2 casas decimais."""
        if v is None:
            return v
        if v.quantize(Decimal('0.01')) != v:
            raise ValueError('O valor deve ter no máximo 2 casas decimais')
        return v

class CustoFixoInDB(CustoFixoBase):
    """Esquema para representação de custos fixos no banco de dados."""
    id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class CustoFixoResponse(CustoFixoInDB):
    """Esquema para resposta de custos fixos."""
    pass

class CustoFixoList(BaseModel):
    """Esquema para lista paginada de custos fixos."""
    items: List[CustoFixoResponse]
    total: int
    skip: int
    limit: int