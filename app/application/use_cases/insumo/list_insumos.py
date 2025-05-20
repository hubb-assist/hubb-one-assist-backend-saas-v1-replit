"""
Caso de uso para listar insumos com filtros e paginação.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.domain.insumo.interfaces import InsumoRepositoryInterface


class ListInsumosUseCase:
    """
    Caso de uso para listar insumos com paginação e filtros.
    
    Implementa a lógica de negócio para listar insumos com vários filtros,
    sem depender de detalhes específicos de banco de dados ou framework.
    """
    
    def __init__(self, insumo_repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com o repositório de insumos.
        
        Args:
            insumo_repository: Repositório de insumos que segue a interface definida
        """
        self.insumo_repository = insumo_repository
    
    def execute(self,
                skip: int = 0,
                limit: int = 100,
                subscriber_id: Optional[UUID] = None,
                filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa o caso de uso de listagem de insumos.
        
        Args:
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros a retornar
            subscriber_id: ID do assinante para filtragem multitenant
            filters: Dicionário com filtros adicionais (nome, categoria, etc.)
            
        Returns:
            Dict[str, Any]: Dicionário contendo a lista de insumos e metadados de paginação
        """
        # Buscar os insumos no repositório
        insumos = self.insumo_repository.list_insumos(
            skip=skip,
            limit=limit,
            subscriber_id=subscriber_id,
            filters=filters
        )
        
        # Contar o total de insumos (para paginação)
        total = self.insumo_repository.count(subscriber_id=subscriber_id, filters=filters)
        
        # Retornar com metadados de paginação
        return {
            "items": insumos,
            "total": total,
            "skip": skip,
            "limit": limit
        }