"""
Interfaces para o domínio de assinantes (Subscriber).

Define os contratos que devem ser implementados pelos repositórios
e outros componentes que interagem com entidades de assinantes.
"""
from uuid import UUID
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from app.domain.subscriber.entities import SubscriberEntity


class SubscriberRepository(ABC):
    """
    Interface do repositório para operações com assinantes.
    
    Define o contrato que deve ser implementado por qualquer
    repositório que manipule entidades SubscriberEntity.
    """
    
    @abstractmethod
    def create(self, subscriber: SubscriberEntity) -> SubscriberEntity:
        """
        Cria um novo assinante no repositório.
        
        Args:
            subscriber: Entidade SubscriberEntity a ser criada
            
        Returns:
            SubscriberEntity: A entidade criada com ID e timestamps atualizados
        """
        pass
    
    @abstractmethod
    def get_by_id(self, subscriber_id: UUID) -> Optional[SubscriberEntity]:
        """
        Busca um assinante pelo ID.
        
        Args:
            subscriber_id: ID do assinante a ser buscado
            
        Returns:
            Optional[SubscriberEntity]: A entidade encontrada ou None se não existir
        """
        pass
    
    @abstractmethod
    def update(self, subscriber: SubscriberEntity) -> SubscriberEntity:
        """
        Atualiza um assinante existente.
        
        Args:
            subscriber: Entidade SubscriberEntity com as atualizações
            
        Returns:
            SubscriberEntity: A entidade atualizada
        """
        pass
    
    @abstractmethod
    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Lista assinantes com paginação e filtros opcionais.
        
        Args:
            skip: Número de registros para pular (para paginação)
            limit: Número máximo de registros a retornar
            filters: Dicionário de filtros a aplicar na busca
            
        Returns:
            Dict[str, Any]: Dicionário contendo itens e metadados de paginação
        """
        pass
    
    @abstractmethod
    def delete(self, subscriber_id: UUID) -> bool:
        """
        Exclui logicamente um assinante (desativa).
        
        Args:
            subscriber_id: ID do assinante a ser excluído
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        pass
    
    @abstractmethod
    def exists_with_cnpj(self, cnpj: str, exclude_id: Optional[UUID] = None) -> bool:
        """
        Verifica se existe um assinante com o CNPJ informado.
        
        Args:
            cnpj: CNPJ a ser verificado
            exclude_id: ID de assinante a ser excluído da verificação (opcional)
            
        Returns:
            bool: True se existe um assinante com o CNPJ, False caso contrário
        """
        pass