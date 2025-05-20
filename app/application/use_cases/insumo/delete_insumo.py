"""
Caso de uso para excluir um insumo (exclusão lógica).
"""
from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class DeleteInsumoUseCase:
    """
    Caso de uso para excluir um insumo (exclusão lógica).
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso.
        
        Args:
            repository: Repositório de insumos
        """
        self.repository = repository
    
    def execute(self, insumo_id: UUID, subscriber_id: UUID) -> None:
        """
        Executa o caso de uso para excluir um insumo (exclusão lógica).
        
        Args:
            insumo_id: ID do insumo a ser excluído
            subscriber_id: ID do assinante proprietário
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        # Excluir logicamente no repositório
        self.repository.delete(insumo_id, subscriber_id)