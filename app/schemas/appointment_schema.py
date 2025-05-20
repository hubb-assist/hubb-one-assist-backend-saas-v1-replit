"""
Schemas Pydantic para Agendamentos (Appointments).
"""
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class AppointmentStatusEnum(str, Enum):
    """Enum para os possíveis status de um agendamento."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class AppointmentBase(BaseModel):
    """Schema base para agendamentos."""
    patient_id: UUID
    provider_id: UUID
    service_id: UUID
    start_time: datetime
    end_time: datetime
    status: AppointmentStatusEnum = AppointmentStatusEnum.SCHEDULED
    notes: Optional[str] = None
    
    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        """Valida que o horário final é posterior ao horário inicial."""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('O horário final deve ser posterior ao horário inicial')
        return v


class AppointmentCreate(AppointmentBase):
    """Schema para criação de agendamentos."""
    pass


class AppointmentUpdate(BaseModel):
    """Schema para atualização de agendamentos."""
    patient_id: Optional[UUID] = None
    provider_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[AppointmentStatusEnum] = None
    notes: Optional[str] = None
    
    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        """Valida que o horário final é posterior ao horário inicial."""
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('O horário final deve ser posterior ao horário inicial')
        return v


class AppointmentResponse(AppointmentBase):
    """Schema para resposta de agendamentos."""
    id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AppointmentList(BaseModel):
    """Schema para lista paginada de agendamentos."""
    items: List[AppointmentResponse]
    total: int
    page: int
    size: int