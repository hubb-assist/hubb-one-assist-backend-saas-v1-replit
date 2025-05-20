"""
Caso de uso para exclusão lógica de um insumo.
"""
from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class DeleteInsumoUseCase:
    """
    Caso de uso para exclusão lógica de um insumo.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso.
        
        Args:
            repository: Repositório de insumos
        """
        self.repository = repository
    
    def execute(self, insumo_id: UUID, subscriber_id: UUID) -> dict:
        """
        Executa o caso de uso para exclusão lógica de um insumo.
        
        Args:
            insumo_id: ID do insumo a ser excluído
            subscriber_id: ID do assinante proprietário para validação
            
        Returns:
            dict: Resposta de sucesso
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        # Verificar se o insumo existe antes da exclusão
        entity = self.repository.get_by_id(insumo_id, subscriber_id)
        
        # Executar a exclusão lógica
        self.repository.delete(insumo_id, subscriber_id)
        
        # Resposta
        return {
            "message": "Insumo excluído com sucesso",
            "id": str(insumo_id),
            "nome": entity.nome
        }