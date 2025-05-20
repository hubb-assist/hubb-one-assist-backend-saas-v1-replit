"""
Caso de uso para obter um insumo pelo ID.
"""

from typing import Optional
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class GetInsumoUseCase:
    """
    Caso de uso para obter um insumo pelo ID.
    
    Implementa a lógica de negócio para recuperar um insumo específico,
    sem depender de detalhes específicos de banco de dados ou framework.
    """
    
    def __init__(self, insumo_repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com o repositório de insumos.
        
        Args:
            insumo_repository: Repositório de insumos que segue a interface definida
        """
        self.insumo_repository = insumo_repository
    
    def execute(self, insumo_id: UUID) -> Optional[InsumoEntity]:
        """
        Executa o caso de uso de busca de insumo pelo ID.
        
        Args:
            insumo_id: UUID do insumo a ser buscado
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo se encontrada, None caso contrário
        """
        # Buscar no repositório
        return self.insumo_repository.get_by_id(insumo_id)