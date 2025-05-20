from typing import Optional
from uuid import UUID

from app.domain.cost_fixed.entities import CostFixedEntity
from app.domain.cost_fixed.interfaces import ICostFixedRepository


class GetCostFixedUseCase:
    """Caso de uso para obter um custo fixo específico."""

    def __init__(self, repository: ICostFixedRepository):
        self.repository = repository

    def execute(self, cost_fixed_id: UUID, subscriber_id: UUID) -> Optional[CostFixedEntity]:
        """
        Obtém um custo fixo pelo seu ID.
        
        Args:
            cost_fixed_id: ID do custo fixo a ser obtido
            subscriber_id: ID do assinante para verificação de permissão
            
        Returns:
            Entidade de custo fixo se encontrada, None caso contrário
            
        Raises:
            ValueError: Se o custo fixo não for encontrado ou não pertencer ao assinante
        """
        cost_fixed = self.repository.get_by_id(cost_fixed_id, subscriber_id)
        
        if not cost_fixed:
            raise ValueError(f"Custo fixo com ID {cost_fixed_id} não encontrado ou não pertence ao assinante")
            
        return cost_fixed