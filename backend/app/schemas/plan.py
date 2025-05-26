"""
Schemas Pydantic para planos
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict, validator, model_validator


class PlanModuleBase(BaseModel):
    """Schema base para vínculo entre plano e módulo"""
    module_id: UUID
    price: float = Field(0.0, ge=0)
    is_free: bool = False
    trial_days: Optional[int] = Field(None, ge=0)

    @validator("trial_days")
    def validate_trial_days(cls, v):
        """Valida que trial_days é positivo se fornecido"""
        if v is not None and v < 0:
            raise ValueError("Dias de teste devem ser um número positivo")
        return v

    @model_validator(mode="after")
    def validate_price_and_free(self):
        """Valida a coerência entre is_free e price"""
        if self.is_free and self.price > 0:
            self.price = 0.0
        return self

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class PlanModuleCreate(PlanModuleBase):
    """Schema para criação de vínculo entre plano e módulo"""
    pass


class PlanModuleResponse(PlanModuleBase):
    """Schema para resposta de vínculo entre plano e módulo"""
    plan_id: UUID
    module_id: UUID

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class PlanBase(BaseModel):
    """Schema base para planos com atributos comuns"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    segment_id: UUID
    base_price: float = Field(..., ge=0)
    is_active: bool = True

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class PlanCreate(PlanBase):
    """Schema para criação de novo plano"""
    modules: Optional[List[PlanModuleCreate]] = []


class PlanUpdate(BaseModel):
    """Schema para atualização de plano - todos os campos são opcionais"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    segment_id: Optional[UUID] = None
    base_price: Optional[float] = Field(None, ge=0)
    is_active: Optional[bool] = None
    modules: Optional[List[PlanModuleCreate]] = None  # Lista de módulos para atualizados

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        extra="forbid"  # impede campos extras
    )


class PlanResponse(PlanBase):
    """Schema para resposta de plano - inclui campos somente leitura"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    modules: List[PlanModuleResponse] = []

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )


class PaginatedPlanResponse(BaseModel):
    """Schema para resposta paginada de planos"""
    total: int
    page: int
    size: int
    items: List[PlanResponse]