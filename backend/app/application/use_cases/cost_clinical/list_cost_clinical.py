from uuid import UUID
from datetime import date
from typing import List, Optional, Dict, Any

from app.domain.cost_clinical.interfaces import ICostClinicalRepository
from app.domain.cost_clinical.entities import CostClinicalEntity

class ListCostClinicalUseCase:
    """
    Caso de uso para listar custos clínicos com paginação e filtro por data.
    """
    
    def __init__(self, repository: ICostClinicalRepository):
        self.repository = repository
    
    def execute(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso.
        
        Args:
            subscriber_id: ID do assinante
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros para retornar (paginação)
            date_from: Data inicial para filtro
            date_to: Data final para filtro
            
        Returns:
            Dicionário com a lista de custos clínicos e informações de paginação
        """
        # Obter os registros
        items = self.repository.list_all(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            date_from=date_from,
            date_to=date_to
        )
        
        # Contar o total de registros
        total = self.repository.count(
            subscriber_id=subscriber_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # Retornar como dicionário para facilitar a serialização
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit
        }