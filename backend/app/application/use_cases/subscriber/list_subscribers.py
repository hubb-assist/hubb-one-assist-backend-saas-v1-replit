"""
Caso de uso para listar assinantes com filtros e paginação.
"""
from typing import Dict, Any, Optional
from uuid import UUID

from app.domain.subscriber.interfaces import SubscriberRepository


class ListSubscribersUseCase:
    """
    Caso de uso para listar assinantes com filtros e paginação.
    
    Implementa a lógica de negócio para listagem de assinantes,
    incluindo paginação e filtros diversos.
    """
    
    def __init__(self, subscriber_repository: SubscriberRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            subscriber_repository: Uma implementação de SubscriberRepository
        """
        self.repository = subscriber_repository
    
    def execute(
        self,
        skip: int = 0,
        limit: int = 10,
        name: Optional[str] = None,
        cnpj: Optional[str] = None,
        segment_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso para listar assinantes com filtros.
        
        Args:
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros a retornar
            name: Filtro por nome (parcial)
            cnpj: Filtro por CNPJ (parcial)
            segment_id: Filtro por ID do segmento
            is_active: Filtro por status de ativação
            
        Returns:
            Dict[str, Any]: Dicionário contendo a lista de assinantes e metadados
                de paginação
        """
        # Prepara filtros para o repositório
        filters = {}
        
        if name:
            filters["name"] = name
        
        if cnpj:
            filters["cnpj"] = cnpj
        
        if segment_id:
            filters["segment_id"] = segment_id
        
        if is_active is not None:
            filters["is_active"] = is_active
        
        # Delega para o repositório a busca com filtros
        result = self.repository.list(skip, limit, filters)
        
        return result