"""
Entidades do domínio de Agendamentos
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from dataclasses import dataclass

@dataclass
class AppointmentEntity:
    """
    Entidade de domínio representando um agendamento
    """
    id: Optional[UUID] = None
    subscriber_id: Optional[UUID] = None
    patient_id: Optional[UUID] = None
    provider_id: Optional[int] = None
    service_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def validate(self) -> bool:
        """
        Valida a entidade de agendamento
        
        Returns:
            bool: True se válido, False caso contrário
        """
        if not self.subscriber_id:
            return False
        
        if not self.patient_id:
            return False
        
        if not self.provider_id:
            return False
        
        if not self.service_name:
            return False
        
        if not self.start_time:
            return False
        
        if not self.end_time:
            return False
        
        if self.start_time >= self.end_time:
            return False
        
        return True
    
    def cancel(self) -> None:
        """
        Cancela o agendamento alterando seu status
        """
        self.status = "cancelled"
        self.updated_at = datetime.now()
    
    def reschedule(self, start_time: datetime, end_time: datetime) -> bool:
        """
        Reagenda o agendamento para um novo horário
        
        Args:
            start_time: Novo horário de início
            end_time: Novo horário de término
            
        Returns:
            bool: True se o reagendamento for válido, False caso contrário
        """
        if start_time >= end_time:
            return False
        
        self.start_time = start_time
        self.end_time = end_time
        self.updated_at = datetime.now()
        
        if self.status in ["cancelled", "completed"]:
            self.status = "rescheduled"
            
        return True