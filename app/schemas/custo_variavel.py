from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

class CustoVariavelBase(BaseModel):
    """Esquema base para custos variáveis."""
    nome: str = Field(..., min_length=1, max_length=255)
    valor_unitario: Decimal = Field(..., gt=0)
    quantidade: int = Field(..., gt=0)
    data: date
    observacoes: Optional[str] = None
    
    @field_validator('valor_unitario')
    @classmethod
    def validate_valor_unitario(cls, v: Decimal) -> Decimal:
        """Valida que o valor unitário tenha no máximo 2 casas decimais."""
        if v.quantize(Decimal('0.01')) != v:
            raise ValueError('O valor unitário deve ter no máximo 2 casas decimais')
        return v

class CustoVariavelCreate(CustoVariavelBase):
    """Esquema para criação de custos variáveis."""
    pass

class CustoVariavelUpdate(BaseModel):
    """Esquema para atualização de custos variáveis."""
    nome: Optional[str] = Field(None, min_length=1, max_length=255)
    valor_unitario: Optional[Decimal] = Field(None, gt=0)
    quantidade: Optional[int] = Field(None, gt=0)
    data: Optional[date] = None
    observacoes: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('valor_unitario')
    @classmethod
    def validate_valor_unitario(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Valida que o valor unitário tenha no máximo 2 casas decimais."""
        if v is None:
            return v
        if v.quantize(Decimal('0.01')) != v:
            raise ValueError('O valor unitário deve ter no máximo 2 casas decimais')
        return v

class CustoVariavelInDB(CustoVariavelBase):
    """Esquema para representação de custos variáveis no banco de dados."""
    id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}

class CustoVariavelResponse(CustoVariavelInDB):
    """Esquema para resposta de custos variáveis."""
    # Valor total calculado (valor_unitario * quantidade)
    valor_total: Decimal = Field(...)
    
    @field_validator('valor_total', mode='before')
    @classmethod
    def calcular_valor_total(cls, v: Any, values: dict) -> Decimal:
        """Calcula o valor total a partir do valor unitário e quantidade."""
        valor_unitario = values.data.get('valor_unitario')
        quantidade = values.data.get('quantidade')
        if valor_unitario is not None and quantidade is not None:
            return valor_unitario * quantidade
        return Decimal('0.00')

class CustoVariavelList(BaseModel):
    """Esquema para lista paginada de custos variáveis."""
    items: List[CustoVariavelResponse]
    total: int
    skip: int
    limit: int