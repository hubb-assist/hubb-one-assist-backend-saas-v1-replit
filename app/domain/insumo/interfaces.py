"""
Interfaces para o domínio de Insumos.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity


class InsumoRepositoryInterface(ABC):
    """
    Interface para o repositório de Insumos.
    """
    
    @abstractmethod
    def create(self, entity: InsumoEntity) -> InsumoEntity:
        """
        Cria um novo insumo no repositório.
        
        Args:
            entity: Entidade de Insumo a ser criada.
            
        Returns:
            InsumoEntity: Entidade criada com ID.
        """
        pass
    
    @abstractmethod
    def get_by_id(self, insumo_id: UUID, subscriber_id: UUID) -> InsumoEntity:
        """
        Obtém um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo a ser obtido.
            subscriber_id: ID do assinante proprietário do insumo.
            
        Returns:
            InsumoEntity: Entidade de Insumo encontrada.
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado.
        """
        pass
    
    @abstractmethod
    def update(self, entity: InsumoEntity) -> InsumoEntity:
        """
        Atualiza um insumo existente.
        
        Args:
            entity: Entidade de Insumo com os dados atualizados.
            
        Returns:
            InsumoEntity: Entidade atualizada.
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado.
        """
        pass
    
    @abstractmethod
    def delete(self, insumo_id: UUID, subscriber_id: UUID) -> None:
        """
        Exclui logicamente um insumo (soft delete).
        
        Args:
            insumo_id: ID do insumo a ser excluído.
            subscriber_id: ID do assinante proprietário do insumo.
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado.
        """
        pass
    
    @abstractmethod
    def list(self, 
             subscriber_id: UUID,
             skip: int = 0,
             limit: int = 100,
             filters: Optional[Dict[str, Any]] = None,
             ) -> List[InsumoEntity]:
        """
        Lista insumos com paginação e filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante proprietário dos insumos.
            skip: Número de registros a pular (para paginação).
            limit: Número máximo de registros a retornar.
            filters: Filtros opcionais a serem aplicados.
            
        Returns:
            List[InsumoEntity]: Lista de entidades de Insumo.
        """
        pass