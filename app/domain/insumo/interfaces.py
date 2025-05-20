"""
Interfaces para o domínio de Insumos.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity


class InsumoRepositoryInterface(ABC):
    """
    Interface para repositório de insumos.
    
    Define os métodos que qualquer implementação de repositório
    de insumos deve fornecer.
    """
    
    @abstractmethod
    def create(self, 
               nome: str,
               descricao: str,
               categoria: str,
               valor_unitario: float,
               unidade_medida: str,
               estoque_minimo: int,
               estoque_atual: int,
               subscriber_id: UUID,
               fornecedor: Optional[str] = None,
               codigo_referencia: Optional[str] = None,
               data_validade: Optional[str] = None,
               data_compra: Optional[str] = None,
               observacoes: Optional[str] = None,
               modules_used: Optional[List[Dict[str, Any]]] = None) -> InsumoEntity:
        """
        Cria um novo insumo.
        
        Args:
            nome: Nome do insumo
            descricao: Descrição detalhada
            categoria: Categoria do insumo
            valor_unitario: Valor unitário
            unidade_medida: Unidade de medida
            estoque_minimo: Estoque mínimo recomendado
            estoque_atual: Estoque atual
            subscriber_id: ID do assinante proprietário
            fornecedor: Nome do fornecedor (opcional)
            codigo_referencia: Código de referência (opcional)
            data_validade: Data de validade (opcional)
            data_compra: Data de compra (opcional)
            observacoes: Observações adicionais (opcional)
            modules_used: Lista de módulos que usam este insumo (opcional)
            
        Returns:
            InsumoEntity: Entidade de insumo criada
        """
        pass
    
    @abstractmethod
    def get_by_id(self, insumo_id: UUID) -> Optional[InsumoEntity]:
        """
        Obtém um insumo pelo ID.
        
        Args:
            insumo_id: UUID do insumo
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo ou None se não encontrado
        """
        pass
    
    @abstractmethod
    def list(self, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Lista insumos com paginação e filtros.
        
        Args:
            skip: Quantos insumos pular (paginação)
            limit: Limite de insumos a retornar
            filters: Filtros a aplicar
            
        Returns:
            Dict[str, Any]: Dicionário com itens, total, skip e limit
        """
        pass
    
    @abstractmethod
    def list_by_subscriber(self, subscriber_id: UUID, skip: int = 0, limit: int = 100, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Lista insumos de um assinante específico.
        
        Args:
            subscriber_id: ID do assinante
            skip: Quantos insumos pular (paginação)
            limit: Limite de insumos a retornar
            filters: Filtros a aplicar
            
        Returns:
            Dict[str, Any]: Dicionário com itens, total, skip e limit
        """
        pass
    
    @abstractmethod
    def update(self, insumo_id: UUID, data: Dict[str, Any]) -> Optional[InsumoEntity]:
        """
        Atualiza um insumo existente.
        
        Args:
            insumo_id: UUID do insumo a atualizar
            data: Dicionário com campos a atualizar
            
        Returns:
            Optional[InsumoEntity]: Entidade atualizada ou None se não encontrado
        """
        pass
    
    @abstractmethod
    def delete(self, insumo_id: UUID) -> bool:
        """
        Exclui logicamente um insumo (soft delete).
        
        Args:
            insumo_id: UUID do insumo a excluir
            
        Returns:
            bool: True se bem-sucedido, False caso contrário
        """
        pass