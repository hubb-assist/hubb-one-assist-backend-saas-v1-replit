"""
Caso de uso para remover (logicamente) um insumo.
"""

from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class DeleteInsumoUseCase:
    """
    Caso de uso para remover (logicamente) um insumo.
    
    Responsável por realizar a exclusão lógica de um insumo,
    marcando-o como inativo sem remover definitivamente do banco de dados.
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
        Executa o caso de uso para remover um insumo.
        
        Args:
            insumo_id: ID do insumo a ser removido
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
            
        Raises:
            ValueError: Se ocorrer um erro durante a remoção
        """
        return self.repository.delete(insumo_id)