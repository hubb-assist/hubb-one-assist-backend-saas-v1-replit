from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import date
from app.domain.cost_fixed.entities import CostFixedEntity


class ICostFixedRepository(ABC):
    """Interface para o repositório de custos fixos."""

    @abstractmethod
    def create(self, cost_fixed: CostFixedEntity) -> CostFixedEntity:
        """Cria um novo registro de custo fixo."""
        pass

    @abstractmethod
    def get_by_id(self, cost_fixed_id: UUID, subscriber_id: UUID) -> Optional[CostFixedEntity]:
        """Obtém um custo fixo pelo seu ID."""
        pass

    @abstractmethod
    def update(self, cost_fixed_id: UUID, cost_fixed_update: dict, subscriber_id: UUID) -> Optional[CostFixedEntity]:
        """Atualiza um custo fixo existente."""
        pass

    @abstractmethod
    def delete(self, cost_fixed_id: UUID, subscriber_id: UUID) -> bool:
        """Remove (desativa) um custo fixo."""
        pass

    @abstractmethod
    def list_all(
        self, 
        subscriber_id: UUID, 
        skip: int = 0, 
        limit: int = 100, 
        date_from: Optional[date] = None, 
        date_to: Optional[date] = None
    ) -> List[CostFixedEntity]:
        """Lista todos os custos fixos de um assinante, com opção de filtro por data."""
        pass

    @abstractmethod
    def count(
        self, 
        subscriber_id: UUID,
        date_from: Optional[date] = None, 
        date_to: Optional[date] = None
    ) -> int:
        """Conta o número total de custos fixos de um assinante."""
        pass