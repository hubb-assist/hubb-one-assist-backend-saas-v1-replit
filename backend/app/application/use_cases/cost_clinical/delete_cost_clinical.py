from uuid import UUID

from app.domain.cost_clinical.interfaces import ICostClinicalRepository

class DeleteCostClinicalUseCase:
    """
    Caso de uso para remover (desativar) um custo clínico.
    """
    
    def __init__(self, repository: ICostClinicalRepository):
        self.repository = repository
    
    def execute(self, id: UUID, subscriber_id: UUID) -> bool:
        """
        Executa o caso de uso.
        
        Args:
            id: ID do custo clínico a ser removido
            subscriber_id: ID do assinante
            
        Returns:
            True se removido com sucesso, False caso contrário
        """
        return self.repository.delete(id, subscriber_id)