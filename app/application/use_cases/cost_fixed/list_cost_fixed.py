from typing import List, Optional
from uuid import UUID
from datetime import date

from app.domain.cost_fixed.entities import CostFixedEntity
from app.domain.cost_fixed.interfaces import ICostFixedRepository


class ListCostFixedUseCase:
    """Caso de uso para listar custos fixos."""

    def __init__(self, repository: ICostFixedRepository):
        self.repository = repository

    def execute(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> tuple[List[CostFixedEntity], int]:
        """
        Lista custos fixos de um assinante com opção de filtro por data.
        
        Args:
            subscriber_id: ID do assinante
            skip: Quantos registros pular (paginação)
            limit: Limite de registros a retornar (paginação)
            date_from: Data inicial para filtro
            date_to: Data final para filtro
            
        Returns:
            Tupla contendo a lista de custos fixos e o total de registros
        """
        items = self.repository.list_all(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            date_from=date_from,
            date_to=date_to
        )
        
        count = self.repository.count(
            subscriber_id=subscriber_id,
            date_from=date_from,
            date_to=date_to
        )
        
        return items, count