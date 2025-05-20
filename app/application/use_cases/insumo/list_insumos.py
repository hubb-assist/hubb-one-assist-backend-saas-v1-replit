"""
Casos de uso para listar insumos.
"""

from typing import Dict, Any, Optional
from uuid import UUID

from app.domain.insumo.interfaces import InsumoRepositoryInterface


class ListInsumosBySubscriberUseCase:
    """
    Caso de uso para listar insumos de um assinante específico.
    
    Permite listar insumos com paginação e filtros opcionais,
    restringindo os resultados aos insumos pertencentes a um assinante.
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            repository: Implementação do repositório de insumos
        """
        self.repository = repository
    
    def execute(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso para listar insumos de um assinante.
        
        Args:
            subscriber_id: ID do assinante para filtrar insumos
            skip: Quantos registros pular para paginação
            limit: Limite de registros a retornar
            filters: Filtros adicionais (nome, categoria, etc.)
            
        Returns:
            Dict[str, Any]: Dicionário com os itens e informações de paginação
        """
        return self.repository.list_by_subscriber(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            filters=filters
        )


class ListInsumosUseCase:
    """
    Caso de uso para listar todos os insumos.
    
    Permite listar insumos com paginação e filtros opcionais,
    sem restrição por assinante (para uso administrativo).
    """
    
    def __init__(self, repository: InsumoRepositoryInterface):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            repository: Implementação do repositório de insumos
        """
        self.repository = repository
    
    def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso para listar todos os insumos.
        
        Args:
            skip: Quantos registros pular para paginação
            limit: Limite de registros a retornar
            filters: Filtros adicionais (nome, categoria, assinante, etc.)
            
        Returns:
            Dict[str, Any]: Dicionário com os itens e informações de paginação
        """
        # Nota: Este método depende da implementação de um método 'list_all' no repositório,
        # que não está definido na interface básica pois é um método administrativo
        # e não estará disponível em todos os repositórios.
        return self.repository.list_by_subscriber(
            subscriber_id=None,  # None indica que não há restrição por assinante
            skip=skip,
            limit=limit,
            filters=filters
        )