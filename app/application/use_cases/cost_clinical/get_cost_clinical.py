from uuid import UUID
from typing import Optional

from app.domain.cost_clinical.interfaces import ICostClinicalRepository
from app.domain.cost_clinical.entities import CostClinicalEntity

class GetCostClinicalUseCase:
    """
    Caso de uso para obter um custo clínico pelo ID.
    """
    
    def __init__(self, repository: ICostClinicalRepository):
        self.repository = repository
    
    def execute(self, id: UUID, subscriber_id: UUID) -> Optional[CostClinicalEntity]:
        """
        Executa o caso de uso.
        
        Args:
            id: ID do custo clínico
            subscriber_id: ID do assinante
            
        Returns:
            Entidade do custo clínico ou None se não encontrado
        """
        return self.repository.get_by_id(id, subscriber_id)