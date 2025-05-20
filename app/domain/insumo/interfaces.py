"""
Interfaces abstratas para repositórios do domínio Insumo.
Seguindo o Princípio de Inversão de Dependência (DIP).
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity
from app.schemas.insumo import InsumoCreate, InsumoUpdate


class InsumoRepository(ABC):
    """
    Repositório abstrato para Insumos.
    Define os métodos que qualquer implementação concreta deve fornecer.
    """
    
    @abstractmethod
    def create(self, insumo_data: InsumoCreate, subscriber_id: UUID) -> InsumoEntity:
        """
        Cria um novo insumo.
        
        Args:
            insumo_data: Dados do insumo a ser criado
            subscriber_id: ID do assinante para associação (multitenancy)
            
        Returns:
            InsumoEntity: Entidade de insumo criada
            
        Raises:
            HTTPException: Se houver algum erro na criação
        """
        pass
    
    @abstractmethod
    def get_by_id(self, insumo_id: UUID, subscriber_id: UUID) -> Optional[InsumoEntity]:
        """
        Busca um insumo pelo seu ID.
        
        Args:
            insumo_id: ID do insumo a ser buscado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo se encontrada, None caso contrário
        """
        pass
    
    @abstractmethod
    def update(self, insumo_id: UUID, insumo_data: InsumoUpdate, subscriber_id: UUID) -> Optional[InsumoEntity]:
        """
        Atualiza um insumo existente.
        
        Args:
            insumo_id: ID do insumo a ser atualizado
            insumo_data: Dados a serem atualizados
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo atualizada, None se não encontrada
            
        Raises:
            HTTPException: Se houver algum erro na atualização
        """
        pass
    
    @abstractmethod
    def delete(self, insumo_id: UUID, subscriber_id: UUID) -> bool:
        """
        Desativa um insumo logicamente.
        
        Args:
            insumo_id: ID do insumo a ser desativado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            bool: True se desativado com sucesso, False caso contrário
        """
        pass
    
    @abstractmethod
    def list_all(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[InsumoEntity]:
        """
        Lista todos os insumos com paginação e filtros opcionais.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenancy)
            skip: Quantidade de registros para pular
            limit: Limite de registros a retornar
            filters: Filtros adicionais como categoria ou módulos
            
        Returns:
            List[InsumoEntity]: Lista de entidades de insumo
        """
        pass
    
    @abstractmethod
    def count(self, subscriber_id: UUID, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta o número total de insumos com base nos filtros.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenancy)
            filters: Filtros adicionais como categoria ou módulos
            
        Returns:
            int: Número total de insumos
        """
        pass