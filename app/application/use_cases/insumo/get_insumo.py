"""
Caso de uso para obter um insumo pelo ID.
"""
from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class GetInsumoUseCase:
    """
    Caso de uso para obter um insumo pelo ID.
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
        Executa o caso de uso para obter um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo a ser obtido
            subscriber_id: ID do assinante proprietário
            
        Returns:
            dict: Dados do insumo encontrado
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        # Buscar no repositório
        entity = self.repository.get_by_id(insumo_id, subscriber_id)
        
        # Retornar como dicionário
        return entity.to_dict()