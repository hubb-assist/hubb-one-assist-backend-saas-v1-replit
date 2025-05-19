"""
Caso de uso para buscar um assinante específico por ID.
"""
from uuid import UUID
from typing import Optional

from fastapi import HTTPException

from app.domain.subscriber.interfaces import SubscriberRepository
from app.domain.subscriber.entities import SubscriberEntity


class GetSubscriberUseCase:
    """
    Caso de uso para buscar um assinante pelo ID.
    
    Implementa a lógica de negócio para busca de assinantes,
    incluindo validações e tratamento de erros.
    """
    
    def __init__(self, subscriber_repository: SubscriberRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            subscriber_repository: Uma implementação de SubscriberRepository
        """
        self.repository = subscriber_repository
    
    def execute(self, subscriber_id: UUID) -> SubscriberEntity:
        """
        Executa o caso de uso para buscar um assinante pelo ID.
        
        Args:
            subscriber_id: ID do assinante a ser buscado
            
        Returns:
            SubscriberEntity: A entidade de assinante encontrada
            
        Raises:
            HTTPException: Se o assinante não for encontrado
        """
        # Busca o assinante no repositório
        subscriber = self.repository.get_by_id(subscriber_id)
        
        # Se não encontrou, lança exceção
        if not subscriber:
            raise HTTPException(
                status_code=404,
                detail=f"Assinante com ID {subscriber_id} não encontrado"
            )
        
        return subscriber