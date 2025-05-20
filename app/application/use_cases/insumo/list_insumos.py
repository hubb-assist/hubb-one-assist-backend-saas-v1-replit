"""
Caso de uso para listar insumos com paginação e filtros.
"""
from uuid import UUID
from typing import List, Dict, Any, Optional, Tuple

from app.domain.insumo.interfaces import InsumoRepository
from app.domain.insumo.entities import InsumoEntity


class ListInsumosUseCase:
    """
    Caso de uso para listar insumos com paginação e filtros.
    """
    
    def __init__(self, insumo_repository: InsumoRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            insumo_repository: Uma implementação de InsumoRepository
        """
        self.repository = insumo_repository
    
    def execute(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[InsumoEntity], int]:
        """
        Executa o caso de uso para listar insumos.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenancy)
            skip: Quantidade de registros para pular
            limit: Limite de registros a retornar
            filters: Filtros adicionais como categoria ou módulos
            
        Returns:
            Tuple[List[InsumoEntity], int]: Lista de entidades de insumo e contagem total
        """
        # Buscar os insumos do repositório
        insumos = self.repository.list_all(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            filters=filters
        )
        
        # Contar o total de insumos (para paginação)
        total_count = self.repository.count(
            subscriber_id=subscriber_id,
            filters=filters
        )
        
        return insumos, total_count