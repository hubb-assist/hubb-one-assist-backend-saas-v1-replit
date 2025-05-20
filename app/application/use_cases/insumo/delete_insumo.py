"""
Caso de uso para exclusão lógica de insumo.
"""

from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class DeleteInsumoUseCase:
    """
    Caso de uso para exclusão lógica de um insumo.
    
    Implementa a lógica de negócio para excluir um insumo,
    sem depender de detalhes específicos de banco de dados ou framework.
    Realiza exclusão lógica (soft delete) mantendo o histórico.
    """
    
    def __init__(self, insumo_repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com o repositório de insumos.
        
        Args:
            insumo_repository: Repositório de insumos que segue a interface definida
        """
        self.insumo_repository = insumo_repository
    
    def execute(self, insumo_id: UUID) -> bool:
        """
        Executa o caso de uso para excluir um insumo logicamente.
        
        Args:
            insumo_id: UUID do insumo a excluir
            
        Returns:
            bool: True se bem-sucedido, False se o insumo não existir
        """
        # Verificar se o insumo existe antes de tentar excluir
        insumo = self.insumo_repository.get_by_id(insumo_id)
        if not insumo:
            return False
            
        # Executar exclusão lógica no repositório
        return self.insumo_repository.delete(insumo_id)