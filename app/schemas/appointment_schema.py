"""
Schemas Pydantic para o módulo de Agendamentos.
"""
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator


class AppointmentBase(BaseModel):
    """
    Esquema base para agendamentos com campos comuns.
    """
    patient_id: UUID = Field(..., description="ID do paciente")
    provider_id: UUID = Field(..., description="ID do profissional (médico, dentista, etc.)")
    service_id: UUID = Field(..., description="ID do serviço/procedimento")
    start_time: datetime = Field(..., description="Data e hora de início")
    end_time: datetime = Field(..., description="Data e hora de término")
    notes: Optional[str] = Field(None, description="Observações adicionais")
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        """Valida que o horário de término é posterior ao de início."""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('O horário de término deve ser posterior ao horário de início')
        return v


class AppointmentCreate(AppointmentBase):
    """
    Esquema para criação de agendamentos.
    """
    status: Optional[str] = Field('scheduled', description="Situação do agendamento")


class AppointmentUpdate(BaseModel):
    """
    Esquema para atualização de agendamentos.
    Todos os campos são opcionais para permitir atualizações parciais.
    """
    patient_id: Optional[UUID] = Field(None, description="ID do paciente")
    provider_id: Optional[UUID] = Field(None, description="ID do profissional")
    service_id: Optional[UUID] = Field(None, description="ID do serviço/procedimento")
    start_time: Optional[datetime] = Field(None, description="Nova data e hora de início")
    end_time: Optional[datetime] = Field(None, description="Nova data e hora de término")
    status: Optional[str] = Field(None, description="Nova situação do agendamento")
    notes: Optional[str] = Field(None, description="Novas observações")
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        """Valida que o horário de término é posterior ao de início, se ambos foram fornecidos."""
        if v and 'start_time' in values and values['start_time'] and v <= values['start_time']:
            raise ValueError('O horário de término deve ser posterior ao horário de início')
        return v
    
    @validator('status')
    def status_must_be_valid(cls, v):
        """Valida que o status fornecido é válido."""
        if v and v not in ['scheduled', 'confirmed', 'cancelled', 'completed', 'no_show']:
            raise ValueError(f'Status inválido: {v}. Deve ser um dos: scheduled, confirmed, cancelled, completed, no_show')
        return v


class AppointmentResponse(AppointmentBase):
    """
    Esquema para resposta de agendamentos.
    """
    id: UUID = Field(..., description="ID único do agendamento")
    subscriber_id: UUID = Field(..., description="ID do assinante (isolamento multitenancy)")
    status: str = Field(..., description="Situação do agendamento")
    is_active: bool = Field(..., description="Indica se o agendamento está ativo")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: Optional[datetime] = Field(None, description="Data da última atualização")
    
    class Config:
        orm_mode = True


class AppointmentPagination(BaseModel):
    """
    Esquema para paginação de agendamentos.
    """
    total: int = Field(..., description="Total de agendamentos encontrados")
    items: List[AppointmentResponse] = Field(..., description="Lista de agendamentos")
    page: int = Field(..., description="Página atual")
    size: int = Field(..., description="Tamanho da página")
    pages: int = Field(..., description="Total de páginas")
    
    class Config:
        schema_extra = {
            "example": {
                "total": 50,
                "items": [
                    {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "subscriber_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "patient_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "provider_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "service_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "start_time": "2025-05-20T14:30:00Z",
                        "end_time": "2025-05-20T15:30:00Z",
                        "status": "scheduled",
                        "notes": "Primeira consulta",
                        "is_active": True,
                        "created_at": "2025-05-18T10:00:00Z",
                        "updated_at": "2025-05-18T10:00:00Z"
                    }
                ],
                "page": 1,
                "size": 10,
                "pages": 5
            }
        }