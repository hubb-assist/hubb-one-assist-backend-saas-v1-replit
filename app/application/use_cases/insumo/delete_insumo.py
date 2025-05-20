"""
Caso de uso para excluir um insumo.
"""

from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class DeleteInsumoUseCase:
    """
    Caso de uso para excluir logicamente um insumo (soft delete).
    
    Permite marcar um insumo como inativo sem removê-lo fisicamente
    do banco de dados, preservando o histórico.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            repository: Implementação do repositório de insumos
        """
        self.repository = repository
    
    def execute(self, insumo_id: UUID) -> bool:
        """
        Executa o caso de uso para excluir logicamente um insumo.
        
        Args:
            insumo_id: ID do insumo a ser excluído
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        return self.repository.delete(insumo_id)