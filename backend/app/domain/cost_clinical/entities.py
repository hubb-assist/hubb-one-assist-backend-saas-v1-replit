from uuid import UUID
from datetime import date, datetime
from typing import Optional
from decimal import Decimal

class CostClinicalEntity:
    """
    Entidade de domínio para custos clínicos.
    """
    def __init__(
        self,
        id: Optional[UUID] = None,
        subscriber_id: UUID = None,
        procedure_name: str = None,
        duration_hours: Decimal = None,
        hourly_rate: Decimal = None,
        total_cost: Decimal = None,
        date: date = None,
        observacoes: Optional[str] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.subscriber_id = subscriber_id
        self.procedure_name = procedure_name
        self.duration_hours = duration_hours
        self.hourly_rate = hourly_rate
        self.total_cost = total_cost if total_cost is not None else self._calculate_total_cost()
        self.date = date
        self.observacoes = observacoes
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
    
    def _calculate_total_cost(self) -> Optional[Decimal]:
        """
        Calcula o custo total com base na duração e valor hora.
        """
        if self.duration_hours is not None and self.hourly_rate is not None:
            return self.duration_hours * self.hourly_rate
        return None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CostClinicalEntity':
        """
        Cria uma instância da entidade a partir de um dicionário.
        """
        return cls(**data)
    
    def to_dict(self) -> dict:
        """
        Converte a entidade para um dicionário.
        """
        return {
            "id": self.id,
            "subscriber_id": self.subscriber_id,
            "procedure_name": self.procedure_name,
            "duration_hours": self.duration_hours,
            "hourly_rate": self.hourly_rate,
            "total_cost": self.total_cost,
            "date": self.date,
            "observacoes": self.observacoes,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def update(self, data: dict) -> None:
        """
        Atualiza a entidade com novos dados.
        """
        for key, value in data.items():
            if hasattr(self, key) and value is not None:
                setattr(self, key, value)
        
        # Recalcular o custo total se duração ou valor hora foram alterados
        if "duration_hours" in data or "hourly_rate" in data:
            self.total_cost = self._calculate_total_cost()