from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

class CostFixedBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    valor: Decimal = Field(..., gt=0, lt=1000000000)
    data: date
    observacoes: Optional[str] = None
    
    @field_validator('valor')
    @classmethod
    def validate_valor(cls, v: Decimal) -> Decimal:
        # Garante que o valor tenha no máximo 2 casas decimais
        if v.quantize(Decimal('0.01')) != v:
            raise ValueError('O valor deve ter no máximo 2 casas decimais')
        return v

class CostFixedCreate(CostFixedBase):
    pass

class CostFixedUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    valor: Optional[Decimal] = Field(None, gt=0, lt=1000000000)
    data: Optional[date] = None
    observacoes: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('valor')
    @classmethod
    def validate_valor(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is None:
            return None
        # Garante que o valor tenha no máximo 2 casas decimais
        if v.quantize(Decimal('0.01')) != v:
            raise ValueError('O valor deve ter no máximo 2 casas decimais')
        return v

class CostFixedInDB(CostFixedBase):
    id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class CostFixedResponse(CostFixedInDB):
    pass

class CostFixedListResponse(BaseModel):
    items: List[CostFixedResponse]
    total: int
    skip: int
    limit: int