"""
Caso de uso para obter um insumo por ID.
"""
from typing import Dict, Any
from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class GetInsumoUseCase:
    """
    Caso de uso para obter um insumo por ID.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso.
        
        Args:
            repository: Repositório de insumos
        """
        self.repository = repository
    
    def execute(self, insumo_id: UUID, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso para obter um insumo por ID.
        
        Args:
            insumo_id: ID do insumo a ser obtido
            subscriber_id: ID do assinante proprietário
            
        Returns:
            Dict[str, Any]: Dados do insumo encontrado
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        # Buscar no repositório
        insumo = self.repository.get_by_id(insumo_id, subscriber_id)
        
        # Retornar os dados
        return insumo.to_dict()