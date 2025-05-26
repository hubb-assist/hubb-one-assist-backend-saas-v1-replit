"""
Esquemas Pydantic para o módulo de Agendamentos
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


class AppointmentBase(BaseModel):
    """
    Modelo base para agendamentos
    
    Attributes:
        patient_id: ID do paciente
        provider_id: ID do profissional
        service_name: Nome do serviço
        start_time: Data e hora de início
        end_time: Data e hora de término
        status: Status do agendamento (scheduled, confirmed, cancelled, completed)
        notes: Observações adicionais
    """
    patient_id: UUID
    provider_id: UUID
    service_name: str = Field(..., min_length=3, max_length=255)
    start_time: datetime
    end_time: datetime
    status: str = Field(default="scheduled", pattern="^(scheduled|confirmed|cancelled|completed)$")
    notes: Optional[str] = None
    
    @validator("end_time")
    def end_time_after_start_time(cls, v, values):
        """
        Valida que a data/hora de término é posterior à data/hora de início
        """
        if "start_time" in values and v <= values["start_time"]:
            raise ValueError("A data/hora de término deve ser posterior à data/hora de início")
        return v


class AppointmentCreate(AppointmentBase):
    """
    Modelo para criação de agendamentos
    """
    pass


class AppointmentUpdate(BaseModel):
    """
    Modelo para atualização de agendamentos
    
    Attributes:
        service_name: Nome do serviço
        start_time: Data e hora de início
        end_time: Data e hora de término
        status: Status do agendamento (scheduled, confirmed, cancelled, completed)
        notes: Observações adicionais
    """
    service_name: Optional[str] = Field(None, min_length=3, max_length=255)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = Field(None, pattern="^(scheduled|confirmed|cancelled|completed)$")
    notes: Optional[str] = None
    
    @validator("end_time")
    def end_time_after_start_time(cls, v, values):
        """
        Valida que a data/hora de término é posterior à data/hora de início
        """
        if v is not None and "start_time" in values and values["start_time"] is not None and v <= values["start_time"]:
            raise ValueError("A data/hora de término deve ser posterior à data/hora de início")
        return v


class AppointmentInDB(AppointmentBase):
    """
    Modelo para agendamentos armazenados no banco
    
    Attributes:
        id: ID único do agendamento
        subscriber_id: ID do assinante (empresa/clínica)
        is_active: Indica se o registro está ativo
        created_at: Data e hora de criação
        updated_at: Data e hora da última atualização
    """
    id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class AppointmentResponse(AppointmentInDB):
    """
    Modelo para resposta de agendamentos
    """
    pass