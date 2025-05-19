"""
Implementação fake do repositório de assinantes para testes unitários.
"""
from uuid import UUID
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.domain.subscriber.interfaces import SubscriberRepository
from app.domain.subscriber.entities import SubscriberEntity


class FakeSubscriberRepository(SubscriberRepository):
    """
    Implementação em memória do repositório de assinantes para uso em testes.
    
    Armazena entidades em um dicionário e simula operações de banco de dados.
    """
    
    def __init__(self):
        """Inicializa o repositório com um dicionário vazio."""
        self.subscribers: Dict[UUID, SubscriberEntity] = {}

    def create(self, subscriber: SubscriberEntity) -> SubscriberEntity:
        """
        Simula a criação de um assinante.
        
        Args:
            subscriber: Entidade SubscriberEntity a ser criada
            
        Returns:
            SubscriberEntity: A entidade criada
        """
        # Atualiza os timestamps
        subscriber.created_at = datetime.utcnow()
        subscriber.updated_at = datetime.utcnow()
        
        # Armazena no dicionário
        self.subscribers[subscriber.id] = subscriber
        
        return subscriber
    
    def get_by_id(self, subscriber_id: UUID) -> Optional[SubscriberEntity]:
        """
        Busca um assinante pelo ID.
        
        Args:
            subscriber_id: ID do assinante a ser buscado
            
        Returns:
            Optional[SubscriberEntity]: A entidade encontrada ou None se não existir
        """
        return self.subscribers.get(subscriber_id)
    
    def update(self, subscriber: SubscriberEntity) -> SubscriberEntity:
        """
        Atualiza um assinante existente.
        
        Args:
            subscriber: Entidade SubscriberEntity com as atualizações
            
        Returns:
            SubscriberEntity: A entidade atualizada
        """
        # Atualiza o timestamp
        subscriber.updated_at = datetime.utcnow()
        
        # Substitui no dicionário
        self.subscribers[subscriber.id] = subscriber
        
        return subscriber
    
    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Lista assinantes com paginação e filtros opcionais.
        
        Args:
            skip: Número de registros para pular
            limit: Número máximo de registros a retornar
            filters: Dicionário de filtros a aplicar
            
        Returns:
            Dict[str, Any]: Dicionário com itens e metadados de paginação
        """
        filters = filters or {}
        
        # Filtragem
        filtered_subscribers = list(self.subscribers.values())
        
        # Aplica filtros se existirem
        if 'name' in filters and filters['name']:
            name_filter = filters['name'].lower()
            filtered_subscribers = [
                s for s in filtered_subscribers 
                if name_filter in s.name.lower()
            ]
        
        if 'cnpj' in filters and filters['cnpj']:
            cnpj_filter = filters['cnpj']
            filtered_subscribers = [
                s for s in filtered_subscribers 
                if s.cnpj and cnpj_filter in s.cnpj
            ]
        
        if 'segment_id' in filters and filters['segment_id']:
            segment_id = filters['segment_id']
            filtered_subscribers = [
                s for s in filtered_subscribers 
                if s.segment_id and str(s.segment_id) == str(segment_id)
            ]
        
        if 'is_active' in filters:
            is_active = filters['is_active']
            filtered_subscribers = [
                s for s in filtered_subscribers 
                if s.is_active == is_active
            ]
        
        # Total de registros após a filtragem
        total = len(filtered_subscribers)
        
        # Paginação
        paginated_subscribers = filtered_subscribers[skip:skip+limit]
        
        # Calcula metadados de paginação
        page = (skip // limit) + 1 if limit else 1
        total_pages = (total + limit - 1) // limit if limit else 1
        
        # Retorna o resultado
        return {
            "items": paginated_subscribers,
            "total": total,
            "page": page,
            "size": limit,
            "pages": total_pages
        }
    
    def delete(self, subscriber_id: UUID) -> bool:
        """
        Exclui logicamente um assinante (desativa).
        
        Args:
            subscriber_id: ID do assinante a ser excluído
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        subscriber = self.get_by_id(subscriber_id)
        if not subscriber:
            return False
        
        subscriber.is_active = False
        subscriber.updated_at = datetime.utcnow()
        
        return True
    
    def exists_with_cnpj(self, cnpj: str, exclude_id: Optional[UUID] = None) -> bool:
        """
        Verifica se existe um assinante com o CNPJ informado.
        
        Args:
            cnpj: CNPJ a ser verificado
            exclude_id: ID de assinante a ser excluído da verificação
            
        Returns:
            bool: True se existe um assinante com o CNPJ, False caso contrário
        """
        for subscriber_id, subscriber in self.subscribers.items():
            if (subscriber.cnpj == cnpj and 
                subscriber.is_active and 
                (not exclude_id or subscriber_id != exclude_id)):
                return True
        
        return False