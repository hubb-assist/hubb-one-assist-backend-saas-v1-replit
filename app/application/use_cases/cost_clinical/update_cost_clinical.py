from uuid import UUID
from typing import Optional

from app.domain.cost_clinical.interfaces import ICostClinicalRepository
from app.domain.cost_clinical.entities import CostClinicalEntity
from app.schemas.custo_clinico import CustoClinicalUpdate

class UpdateCostClinicalUseCase:
    """
    Caso de uso para atualizar um custo clínico.
    """
    
    def __init__(self, repository: ICostClinicalRepository):
        self.repository = repository
    
    def execute(self, id: UUID, data: CustoClinicalUpdate, subscriber_id: UUID) -> Optional[CostClinicalEntity]:
        """
        Executa o caso de uso.
        
        Args:
            id: ID do custo clínico a ser atualizado
            data: Dados para atualização
            subscriber_id: ID do assinante
            
        Returns:
            Entidade do custo clínico atualizada ou None se não encontrado
        """
        return self.repository.update(id, data, subscriber_id)