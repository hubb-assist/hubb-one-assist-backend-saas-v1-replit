"""
Interfaces para o domínio de Insumo.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity


class InsumoRepositoryInterface(ABC):
    """
    Interface do repositório para o domínio de Insumo.
    
    Define os métodos que qualquer implementação de repositório
    de insumos deve fornecer.
    """
    
    @abstractmethod
    def create(self, entity: InsumoEntity) -> InsumoEntity:
        """
        Cria um novo insumo no repositório.
        
        Args:
            entity: Entidade de insumo a ser criada
            
        Returns:
            InsumoEntity: Entidade criada, com ID atribuído
        """
        pass
    
    @abstractmethod
    def get_by_id(self, insumo_id: UUID) -> Optional[InsumoEntity]:
        """
        Busca um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo a ser buscado
            
        Returns:
            Optional[InsumoEntity]: Entidade encontrada ou None se não existir
        """
        pass
    
    @abstractmethod
    def list(self, subscriber_id: UUID, filters: Dict[str, Any] = None) -> List[InsumoEntity]:
        """
        Lista insumos com filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante para filtrar insumos
            filters: Dicionário de filtros a serem aplicados
            
        Returns:
            List[InsumoEntity]: Lista de entidades de insumo
        """
        pass
    
    @abstractmethod
    def update(self, entity: InsumoEntity) -> InsumoEntity:
        """
        Atualiza um insumo existente.
        
        Args:
            entity: Entidade de insumo com dados atualizados
            
        Returns:
            InsumoEntity: Entidade atualizada
            
        Raises:
            ValueError: Se o insumo não existir
        """
        pass
    
    @abstractmethod
    def delete(self, insumo_id: UUID) -> bool:
        """
        Remove logicamente um insumo (marcando como inativo).
        
        Args:
            insumo_id: ID do insumo a ser removido
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
        """
        pass
    
    @abstractmethod
    def update_stock(self, insumo_id: UUID, quantidade: int, tipo_movimento: str, 
                    motivo: Optional[str] = None, observacao: Optional[str] = None, 
                    usuario_id: Optional[UUID] = None) -> InsumoEntity:
        """
        Atualiza o estoque de um insumo.
        
        Args:
            insumo_id: ID do insumo a ter estoque atualizado
            quantidade: Quantidade a ser adicionada ou removida
            tipo_movimento: 'entrada' para adicionar ou 'saida' para remover
            motivo: Motivo da movimentação de estoque (opcional)
            observacao: Observação adicional sobre a movimentação (opcional)
            usuario_id: ID do usuário que realizou a movimentação (opcional)
            
        Returns:
            InsumoEntity: Entidade atualizada
            
        Raises:
            ValueError: Se o insumo não existir ou operação inválida
        """
        pass
    
    @abstractmethod
    def get_movimentacoes(
        self, 
        subscriber_id: UUID, 
        insumo_id: Optional[UUID] = None,
        tipo_movimento: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Lista o histórico de movimentações de estoque de insumos com filtros.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenant)
            insumo_id: Filtrar por ID do insumo específico (opcional)
            tipo_movimento: Filtrar por tipo de movimento ('entrada' ou 'saida') (opcional)
            data_inicio: Filtrar por data inicial (opcional)
            data_fim: Filtrar por data final (opcional)
            skip: Quantos registros pular (paginação)
            limit: Limite de registros a retornar (paginação)
            
        Returns:
            Tuple[List[Dict[str, Any]], int]: Lista de movimentações e contagem total
        """
        pass