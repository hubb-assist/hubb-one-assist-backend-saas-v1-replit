from uuid import UUID
from datetime import datetime
from typing import Optional

class AnamnesisEntity:
    """
    Entidade de domínio para Anamnese.
    Representa o histórico de queixa e informações médicas de um paciente.
    """
    
    def __init__(
        self,
        id: Optional[UUID] = None,
        subscriber_id: UUID = None,
        patient_id: UUID = None,
        chief_complaint: str = None,
        medical_history: Optional[str] = None,
        allergies: Optional[str] = None,
        medications: Optional[str] = None,
        notes: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.subscriber_id = subscriber_id
        self.patient_id = patient_id
        self.chief_complaint = chief_complaint
        self.medical_history = medical_history
        self.allergies = allergies
        self.medications = medications
        self.notes = notes
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        
        self._validate()
    
    def _validate(self) -> None:
        """Validações de regras de negócio"""
        if self.chief_complaint is None or len(self.chief_complaint.strip()) < 3:
            raise ValueError("A queixa principal é obrigatória e deve ter pelo menos 3 caracteres")
        
        if self.subscriber_id is None:
            raise ValueError("O ID do assinante é obrigatório")
            
        if self.patient_id is None:
            raise ValueError("O ID do paciente é obrigatório")
    
    def to_dict(self) -> dict:
        """Converte a entidade para um dicionário"""
        return {
            "id": self.id,
            "subscriber_id": self.subscriber_id,
            "patient_id": self.patient_id,
            "chief_complaint": self.chief_complaint,
            "medical_history": self.medical_history,
            "allergies": self.allergies,
            "medications": self.medications,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    def update(self, data: dict) -> None:
        """Atualiza a entidade com novos dados"""
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        
        self._validate()
    
    def deactivate(self) -> None:
        """Desativa logicamente o registro"""
        self.is_active = False