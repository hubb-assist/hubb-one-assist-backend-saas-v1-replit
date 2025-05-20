"""
Esquemas Pydantic para o módulo de Agendamentos
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator

class AppointmentBase(BaseModel):
    """
    Esquema base para agendamentos
    """
    patient_id: UUID = Field(..., description="ID do paciente")
    provider_id: int = Field(..., description="ID do profissional")
    service_name: str = Field(..., description="Nome do serviço")
    start_time: datetime = Field(..., description="Data e hora de início")
    end_time: datetime = Field(..., description="Data e hora de término")
    notes: Optional[str] = Field(None, description="Observações adicionais")
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        """
        Valida se o horário de término é posterior ao de início
        """
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('O horário de término deve ser posterior ao horário de início')
        return v
    
class AppointmentCreate(AppointmentBase):
    """
    Esquema para criação de agendamentos
    """
    status: Optional[str] = Field("scheduled", description="Status do agendamento")
    
class AppointmentUpdate(BaseModel):
    """
    Esquema para atualização de agendamentos
    """
    patient_id: Optional[UUID] = Field(None, description="ID do paciente")
    provider_id: Optional[int] = Field(None, description="ID do profissional")
    service_name: Optional[str] = Field(None, description="Nome do serviço")
    start_time: Optional[datetime] = Field(None, description="Data e hora de início")
    end_time: Optional[datetime] = Field(None, description="Data e hora de término")
    status: Optional[str] = Field(None, description="Status do agendamento")
    notes: Optional[str] = Field(None, description="Observações adicionais")
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        """
        Valida se o horário de término é posterior ao de início, quando ambos estão presentes
        """
        if v is None:
            return v
            
        start_time = values.get('start_time')
        if start_time and v <= start_time:
            raise ValueError('O horário de término deve ser posterior ao horário de início')
        return v
    
class AppointmentResponse(AppointmentBase):
    """
    Esquema para resposta de agendamentos
    """
    id: UUID
    subscriber_id: UUID
    status: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True