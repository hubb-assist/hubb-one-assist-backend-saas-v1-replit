from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

# Esquema base para anamnese
class AnamnesisBase(BaseModel):
    chief_complaint: str = Field(..., min_length=3, description="Queixa principal do paciente")
    medical_history: Optional[str] = Field(None, description="Histórico médico do paciente")
    allergies: Optional[str] = Field(None, description="Alergias do paciente")
    medications: Optional[str] = Field(None, description="Medicamentos em uso pelo paciente")
    notes: Optional[str] = Field(None, description="Observações adicionais")

# Esquema para criação de anamnese
class AnamnesisCreate(AnamnesisBase):
    pass

# Esquema para atualização de anamnese (todos campos opcionais)
class AnamnesisUpdate(BaseModel):
    chief_complaint: Optional[str] = Field(None, min_length=3, description="Queixa principal do paciente")
    medical_history: Optional[str] = Field(None, description="Histórico médico do paciente")
    allergies: Optional[str] = Field(None, description="Alergias do paciente")
    medications: Optional[str] = Field(None, description="Medicamentos em uso pelo paciente")
    notes: Optional[str] = Field(None, description="Observações adicionais")
    is_active: Optional[bool] = Field(None, description="Estado de ativação do registro")

# Esquema de resposta para anamnese
class AnamnesisResponse(AnamnesisBase):
    id: UUID
    subscriber_id: UUID
    patient_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Esquema para listagem paginada de anamneses
class AnamnesisListResponse(BaseModel):
    items: List[AnamnesisResponse]
    total: int