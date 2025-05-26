from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import date, datetime
from uuid import UUID
from typing import Optional, List

class CustoClinicalBase(BaseModel):
    """Esquema base para custos clínicos."""
    procedure_name: str = Field(..., min_length=1, max_length=255)
    duration_hours: Decimal = Field(..., gt=0)
    hourly_rate: Decimal = Field(..., gt=0)
    date: date
    observacoes: Optional[str] = None
    
    @field_validator('duration_hours')
    @classmethod
    def validate_duration_hours(cls, v: Decimal) -> Decimal:
        """Valida que a duração tenha no máximo 2 casas decimais."""
        if v.quantize(Decimal('0.01')) != v:
            raise ValueError('A duração deve ter no máximo 2 casas decimais')
        return v
        
    @field_validator('hourly_rate')
    @classmethod
    def validate_hourly_rate(cls, v: Decimal) -> Decimal:
        """Valida que o valor da hora tenha no máximo 2 casas decimais."""
        if v.quantize(Decimal('0.01')) != v:
            raise ValueError('O valor da hora deve ter no máximo 2 casas decimais')
        return v

class CustoClinicalCreate(CustoClinicalBase):
    """Esquema para criação de custos clínicos."""
    pass

class CustoClinicalUpdate(BaseModel):
    """Esquema para atualização de custos clínicos."""
    procedure_name: Optional[str] = Field(None, min_length=1, max_length=255)
    duration_hours: Optional[Decimal] = Field(None, gt=0)
    hourly_rate: Optional[Decimal] = Field(None, gt=0)
    date: Optional[date] = None
    observacoes: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('duration_hours')
    @classmethod
    def validate_duration_hours(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Valida que a duração tenha no máximo 2 casas decimais."""
        if v is None:
            return v
        if v.quantize(Decimal('0.01')) != v:
            raise ValueError('A duração deve ter no máximo 2 casas decimais')
        return v
        
    @field_validator('hourly_rate')
    @classmethod
    def validate_hourly_rate(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Valida que o valor da hora tenha no máximo 2 casas decimais."""
        if v is None:
            return v
        if v.quantize(Decimal('0.01')) != v:
            raise ValueError('O valor da hora deve ter no máximo 2 casas decimais')
        return v

class CustoClinicalInDB(CustoClinicalBase):
    """Esquema para representação de custos clínicos no banco de dados."""
    id: UUID
    subscriber_id: UUID
    total_cost: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class CustoClinicalResponse(CustoClinicalInDB):
    """Esquema para resposta de custos clínicos."""
    pass

class CustoClinicalList(BaseModel):
    """Esquema para lista paginada de custos clínicos."""
    items: List[CustoClinicalResponse]
    total: int
    skip: int
    limit: int