"""
Esquemas Pydantic para validação e serialização dos dados de agendamento
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class AppointmentBase(BaseModel):
    """Base schema com campos comuns para criação e resposta"""
    patient_id: UUID
    provider_id: UUID
    service_name: str = Field(..., min_length=3, max_length=255)
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        """Validar que o horário de término é posterior ao de início"""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('O horário de término deve ser posterior ao horário de início')
        return v


class AppointmentCreate(AppointmentBase):
    """Schema para criação de agendamento"""
    pass


class AppointmentUpdate(BaseModel):
    """Schema para atualização parcial de agendamento"""
    patient_id: Optional[UUID] = None
    provider_id: Optional[UUID] = None
    service_name: Optional[str] = Field(None, min_length=3, max_length=255)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = Field(None, regex='^(scheduled|confirmed|cancelled|completed)$')
    notes: Optional[str] = None

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        """Validar que o horário de término é posterior ao de início, se fornecido"""
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('O horário de término deve ser posterior ao horário de início')
        return v


class AppointmentResponse(AppointmentBase):
    """Schema para resposta com agendamento"""
    id: UUID
    subscriber_id: UUID
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True