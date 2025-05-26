from uuid import UUID
from typing import Optional

from app.domain.cost_clinical.interfaces import ICostClinicalRepository
from app.domain.cost_clinical.entities import CostClinicalEntity
from app.schemas.custo_clinico import CustoClinicalCreate

class CreateCostClinicalUseCase:
    """
    Caso de uso para criar um custo clínico.
    """
    
    def __init__(self, repository: ICostClinicalRepository):
        self.repository = repository
    
    def execute(self, data: CustoClinicalCreate, subscriber_id: UUID) -> CostClinicalEntity:
        """
        Executa o caso de uso.
        
        Args:
            data: Dados do custo clínico a ser criado
            subscriber_id: ID do assinante
            
        Returns:
            Entidade do custo clínico criado
        """
        return self.repository.create(data, subscriber_id)