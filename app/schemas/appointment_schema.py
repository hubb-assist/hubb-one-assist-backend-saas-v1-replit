"""
Schemas Pydantic para o módulo de Agendamentos
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator

class AppointmentBase(BaseModel):
    """Schema base para agendamentos"""
    patient_id: UUID
    provider_id: int
    service_name: str
    start_time: datetime
    end_time: datetime
    notes: Optional[str] = None
    status: str = "scheduled"

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        """Valida que o horário de término é após o horário de início"""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('O horário de término deve ser após o horário de início')
        return v

class AppointmentCreate(AppointmentBase):
    """Schema para criação de agendamentos"""
    pass

class AppointmentUpdate(BaseModel):
    """Schema para atualização de agendamentos"""
    patient_id: Optional[UUID] = None
    provider_id: Optional[int] = None
    service_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[str] = None

    @validator('end_time')
    def end_time_after_start_time(cls, v, values):
        """Valida que o horário de término é após o horário de início"""
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('O horário de término deve ser após o horário de início')
        return v

class AppointmentResponse(AppointmentBase):
    """Schema para resposta de agendamentos"""
    id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Configuração do schema"""
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
            UUID: lambda uuid: str(uuid)
        }