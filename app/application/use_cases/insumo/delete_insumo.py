"""
Caso de uso para excluir (soft delete) um insumo existente.
"""

from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class DeleteInsumoUseCase:
    """
    Caso de uso para exclusão lógica (soft delete) de um insumo.
    
    Implementa a lógica de negócio para marcar um insumo como inativo,
    sem depender de detalhes específicos de banco de dados ou framework.
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
        Executa o caso de uso de exclusão lógica de insumo.
        
        Args:
            insumo_id: UUID do insumo a ser excluído
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        # Verificar se o insumo existe
        insumo = self.insumo_repository.get_by_id(insumo_id)
        if not insumo:
            return False
        
        # Realizar a exclusão lógica (soft delete)
        return self.insumo_repository.delete(insumo_id)