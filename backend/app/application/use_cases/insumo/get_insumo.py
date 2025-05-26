"""
Caso de uso para obter um insumo específico.
"""

from typing import Optional
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class GetInsumoUseCase:
    """
    Caso de uso para obter um insumo específico pelo ID.
    
    Responsável por buscar um insumo pelo ID através do repositório
    e retornar a entidade correspondente.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            repository: Implementação do repositório de insumos
        """
        self.repository = repository
    
    def execute(self, insumo_id: UUID) -> Optional[InsumoEntity]:
        """
        Executa o caso de uso para obter um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo a buscar
            
        Returns:
            Optional[InsumoEntity]: Entidade encontrada ou None se não existir
            
        Raises:
            ValueError: Se ocorrer um erro durante a busca
        """
        return self.repository.get_by_id(insumo_id)