"""
Interfaces para o domínio de insumos.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity


class InsumoRepositoryInterface(ABC):
    """
    Interface de repositório para insumos.
    """
    
    @abstractmethod
    def create(self, entity: InsumoEntity) -> InsumoEntity:
        """
        Cria um novo insumo.
        
        Args:
            entity: Entidade de insumo a ser criada
            
        Returns:
            InsumoEntity: Entidade de insumo criada com ID gerado
            
        Raises:
            ValueError: Se houver validação inválida
        """
        pass
    
    @abstractmethod
    def get_by_id(self, insumo_id: UUID, subscriber_id: UUID) -> InsumoEntity:
        """
        Obtém um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo a ser obtido
            subscriber_id: ID do assinante proprietário para validação
            
        Returns:
            InsumoEntity: Entidade de insumo encontrada
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        pass
    
    @abstractmethod
    def update(self, entity: InsumoEntity) -> InsumoEntity:
        """
        Atualiza um insumo existente.
        
        Args:
            entity: Entidade de insumo atualizada
            
        Returns:
            InsumoEntity: Entidade de insumo atualizada
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
            ValueError: Se houver validação inválida
        """
        pass
    
    @abstractmethod
    def delete(self, insumo_id: UUID, subscriber_id: UUID) -> None:
        """
        Exclui logicamente um insumo (marca como inativo).
        
        Args:
            insumo_id: ID do insumo a ser excluído
            subscriber_id: ID do assinante proprietário para validação
            
        Raises:
            EntityNotFoundException: Se o insumo não for encontrado
        """
        pass
    
    @abstractmethod
    def list_by_subscriber(
        self, 
        subscriber_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        categoria: Optional[str] = None,
        tipo: Optional[str] = None,
        modulo_id: Optional[UUID] = None,
        is_active: bool = True
    ) -> List[InsumoEntity]:
        """
        Lista insumos de um assinante com filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante proprietário
            skip: Quantidade de registros para pular (para paginação)
            limit: Limite de registros retornados (para paginação)
            categoria: Filtro opcional por categoria
            tipo: Filtro opcional por tipo
            modulo_id: Filtro opcional por módulo
            is_active: Filtro por status de ativação (padrão: True)
            
        Returns:
            List[InsumoEntity]: Lista de entidades de insumo
        """
        pass