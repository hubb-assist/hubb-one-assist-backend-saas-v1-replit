"""
Interfaces para o módulo de Insumos.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity


class InsumoRepositoryInterface(ABC):
    """
    Interface para o repositório de insumos.
    
    Define contratos para todas as operações de persistência relacionadas a insumos,
    permitindo diferentes implementações (SQLAlchemy, MongoDB, etc.) conforme necessário.
    """
    
    @abstractmethod
    def create(self, insumo: InsumoEntity) -> InsumoEntity:
        """
        Cria um novo insumo.
        
        Args:
            insumo: Entidade de insumo a ser criada
            
        Returns:
            InsumoEntity: Entidade criada com ID gerado
        """
        pass
    
    @abstractmethod
    def get_by_id(self, insumo_id: UUID) -> Optional[InsumoEntity]:
        """
        Busca um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo a buscar
            
        Returns:
            Optional[InsumoEntity]: Entidade encontrada ou None
        """
        pass
    
    @abstractmethod
    def list_by_subscriber(
        self, 
        subscriber_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Lista insumos de um assinante com paginação e filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante
            skip: Quantos registros pular
            limit: Limite de registros a retornar
            filters: Filtros a aplicar (nome, categoria, etc.)
            
        Returns:
            Dict[str, Any]: Dicionário com itens e informações de paginação
        """
        pass
    
    @abstractmethod
    def update(self, insumo_id: UUID, data: Dict[str, Any]) -> Optional[InsumoEntity]:
        """
        Atualiza um insumo existente.
        
        Args:
            insumo_id: ID do insumo a atualizar
            data: Dicionário com os campos a atualizar
            
        Returns:
            Optional[InsumoEntity]: Entidade atualizada ou None
        """
        pass
    
    @abstractmethod
    def delete(self, insumo_id: UUID) -> bool:
        """
        Exclui um insumo (pode ser soft delete).
        
        Args:
            insumo_id: ID do insumo a excluir
            
        Returns:
            bool: True se excluído com sucesso, False caso contrário
        """
        pass
    
    @abstractmethod
    def update_estoque(
        self, 
        insumo_id: UUID, 
        quantidade: int,
        tipo_movimento: str,
        observacao: Optional[str] = None
    ) -> Optional[InsumoEntity]:
        """
        Atualiza o estoque de um insumo (entrada ou saída).
        
        Args:
            insumo_id: ID do insumo
            quantidade: Quantidade a adicionar/remover
            tipo_movimento: 'entrada' ou 'saida'
            observacao: Observação opcional sobre o movimento
            
        Returns:
            Optional[InsumoEntity]: Entidade atualizada ou None
        """
        pass