"""
Interfaces para o domínio de Insumos, definindo contratos de repositórios.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity


class InsumoRepositoryInterface(ABC):
    """
    Interface que define os métodos necessários para um repositório de insumos.
    
    Esta interface segue o Princípio de Inversão de Dependência (DIP) do SOLID,
    permitindo que a lógica de domínio dependa apenas de abstrações.
    """
    
    @abstractmethod
    def create(self, insumo: InsumoEntity) -> InsumoEntity:
        """
        Cria um novo insumo no repositório.
        
        Args:
            insumo: A entidade de insumo a ser criada
            
        Returns:
            InsumoEntity: A entidade criada, com ID gerado
            
        Raises:
            ValueError: Se houver um erro ao criar o insumo
        """
        pass
    
    @abstractmethod
    def get_by_id(self, insumo_id: UUID) -> Optional[InsumoEntity]:
        """
        Busca um insumo pelo ID.
        
        Args:
            insumo_id: O ID do insumo a buscar
            
        Returns:
            Optional[InsumoEntity]: A entidade encontrada ou None se não existir
            
        Raises:
            ValueError: Se ocorrer um erro durante a busca
        """
        pass
    
    @abstractmethod
    def list_by_subscriber(
        self, 
        subscriber_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Lista insumos de um assinante com paginação e filtros.
        
        Args:
            subscriber_id: ID do assinante proprietário
            skip: Quantos registros pular (para paginação)
            limit: Limite de registros por página
            filters: Dicionário com filtros a aplicar
            
        Returns:
            Dict[str, Any]: Dicionário com itens e metadados de paginação
            
        Raises:
            ValueError: Se ocorrer um erro durante a listagem
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
            Optional[InsumoEntity]: A entidade atualizada ou None se não encontrada
            
        Raises:
            ValueError: Se ocorrer um erro durante a atualização
        """
        pass
    
    @abstractmethod
    def delete(self, insumo_id: UUID) -> bool:
        """
        Remove (logicamente) um insumo.
        
        Args:
            insumo_id: ID do insumo a remover
            
        Returns:
            bool: True se removido com sucesso, False se não encontrado
            
        Raises:
            ValueError: Se ocorrer um erro durante a remoção
        """
        pass
    
    @abstractmethod
    def update_stock(self, insumo_id: UUID, quantidade: int, tipo_movimento: str) -> Optional[InsumoEntity]:
        """
        Atualiza o estoque de um insumo.
        
        Args:
            insumo_id: ID do insumo a atualizar
            quantidade: Quantidade a ser movimentada (sempre positiva)
            tipo_movimento: Tipo de movimento ('entrada' ou 'saida')
            
        Returns:
            Optional[InsumoEntity]: A entidade atualizada ou None se não encontrada
            
        Raises:
            ValueError: Se ocorrer um erro durante a atualização
            ValueError: Se a quantidade for negativa ou tipo de movimento inválido
            ValueError: Se a retirada resultar em estoque negativo
        """
        pass