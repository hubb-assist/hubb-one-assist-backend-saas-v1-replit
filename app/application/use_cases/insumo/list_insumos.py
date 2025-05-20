"""
Caso de uso para listar insumos com paginação e filtros.
"""

from typing import Dict, Any, Optional
from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class ListInsumosUseCase:
    """
    Caso de uso para listar insumos com paginação e filtros.
    
    Implementa a lógica de negócio para listar insumos,
    sem depender de detalhes específicos de banco de dados ou framework.
    """
    
    def __init__(self, insumo_repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com o repositório de insumos.
        
        Args:
            insumo_repository: Repositório de insumos que segue a interface definida
        """
        self.insumo_repository = insumo_repository
    
    def execute(self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa o caso de uso para listar insumos.
        
        Args:
            skip: Quantos insumos pular (paginação)
            limit: Limite de insumos a retornar
            filters: Filtros a aplicar (opcional)
            
        Returns:
            Dict[str, Any]: Dicionário com itens, total, skip e limit
        """
        # Aplicar valor padrão para filters se for None
        if filters is None:
            filters = {}
        
        return self.insumo_repository.list(skip=skip, limit=limit, filters=filters)


class ListInsumosBySubscriberUseCase:
    """
    Caso de uso para listar insumos de um assinante específico.
    
    Implementa a lógica de negócio para listar insumos de um assinante,
    sem depender de detalhes específicos de banco de dados ou framework.
    """
    
    def __init__(self, insumo_repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com o repositório de insumos.
        
        Args:
            insumo_repository: Repositório de insumos que segue a interface definida
        """
        self.insumo_repository = insumo_repository
    
    def execute(self, subscriber_id: UUID, skip: int = 0, limit: int = 100, 
               filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa o caso de uso para listar insumos de um assinante.
        
        Args:
            subscriber_id: ID do assinante
            skip: Quantos insumos pular (paginação)
            limit: Limite de insumos a retornar
            filters: Filtros a aplicar (opcional)
            
        Returns:
            Dict[str, Any]: Dicionário com itens, total, skip e limit
        """
        # Aplicar valor padrão para filters se for None
        if filters is None:
            filters = {}
        
        return self.insumo_repository.list_by_subscriber(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            filters=filters
        )