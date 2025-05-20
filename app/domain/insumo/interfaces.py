"""
Interfaces para o domínio de Insumos.
Define contratos que a camada de infraestrutura deve implementar.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.domain.insumo.entities import InsumoEntity


class InsumoRepositoryInterface(ABC):
    """
    Interface para repositório de Insumos.
    Define o contrato que qualquer implementação de repositório deve seguir.
    """
    
    @abstractmethod
    def create(self, insumo: InsumoEntity) -> InsumoEntity:
        """
        Cria um novo insumo no repositório.
        
        Args:
            insumo: Entidade de insumo a ser criada
            
        Returns:
            InsumoEntity: Entidade de insumo criada com ID gerado
        """
        pass
    
    @abstractmethod
    def get_by_id(self, insumo_id: UUID) -> Optional[InsumoEntity]:
        """
        Busca um insumo pelo ID.
        
        Args:
            insumo_id: UUID do insumo
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo se encontrada, None caso contrário
        """
        pass
    
    @abstractmethod
    def list_insumos(self, 
                     skip: int = 0, 
                     limit: int = 100,
                     subscriber_id: Optional[UUID] = None,
                     filters: Optional[Dict[str, Any]] = None) -> List[InsumoEntity]:
        """
        Lista insumos com paginação e filtros opcionais.
        
        Args:
            skip: Número de registros para pular (paginação)
            limit: Número máximo de registros a retornar
            subscriber_id: Filtrar por ID do assinante (multitenant)
            filters: Filtros adicionais como categoria, nome, etc.
            
        Returns:
            List[InsumoEntity]: Lista de entidades de insumo
        """
        pass
    
    @abstractmethod
    def update(self, insumo_id: UUID, data: Dict[str, Any]) -> Optional[InsumoEntity]:
        """
        Atualiza um insumo existente.
        
        Args:
            insumo_id: UUID do insumo a ser atualizado
            data: Dicionário com os campos a serem atualizados
            
        Returns:
            Optional[InsumoEntity]: Entidade de insumo atualizada se encontrada, None caso contrário
        """
        pass
    
    @abstractmethod
    def delete(self, insumo_id: UUID) -> bool:
        """
        Exclui logicamente um insumo (soft delete).
        
        Args:
            insumo_id: UUID do insumo a ser excluído
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        pass
    
    @abstractmethod
    def count(self, 
              subscriber_id: Optional[UUID] = None,
              filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta o número total de insumos com filtros opcionais.
        
        Args:
            subscriber_id: Filtrar por ID do assinante (multitenant)
            filters: Filtros adicionais
            
        Returns:
            int: Número total de insumos
        """
        pass