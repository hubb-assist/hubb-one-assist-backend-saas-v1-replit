from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class AnamnesisBase(BaseModel):
    """Esquema base para anamnese"""
    chief_complaint: str = Field(
        ..., 
        description="Queixa principal do paciente",
        min_length=3
    )
    medical_history: Optional[str] = Field(
        None, 
        description="Histórico médico do paciente"
    )
    allergies: Optional[str] = Field(
        None, 
        description="Lista de alergias do paciente"
    )
    medications: Optional[str] = Field(
        None, 
        description="Medicamentos que o paciente está tomando atualmente"
    )
    notes: Optional[str] = Field(
        None, 
        description="Observações adicionais"
    )


class AnamnesisCreate(AnamnesisBase):
    """Esquema para criação de anamnese"""
    pass


class AnamnesisUpdate(BaseModel):
    """Esquema para atualização de anamnese"""
    chief_complaint: Optional[str] = Field(
        None, 
        description="Queixa principal do paciente",
        min_length=3
    )
    medical_history: Optional[str] = Field(
        None, 
        description="Histórico médico do paciente"
    )
    allergies: Optional[str] = Field(
        None, 
        description="Lista de alergias do paciente"
    )
    medications: Optional[str] = Field(
        None, 
        description="Medicamentos que o paciente está tomando atualmente"
    )
    notes: Optional[str] = Field(
        None, 
        description="Observações adicionais"
    )
    
    model_config = ConfigDict(extra="forbid")


class AnamnesisResponse(AnamnesisBase):
    """Esquema para resposta de anamnese"""
    id: UUID
    patient_id: UUID
    subscriber_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }
    )


class AnamnesisListResponse(BaseModel):
    """Esquema para resposta de lista de anamneses"""
    items: List[AnamnesisResponse]
    total: int