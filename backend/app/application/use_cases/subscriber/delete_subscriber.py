"""
Caso de uso para exclusão lógica de um assinante.
"""
from uuid import UUID

from fastapi import HTTPException

from app.domain.subscriber.interfaces import SubscriberRepository


class DeleteSubscriberUseCase:
    """
    Caso de uso para desativar (exclusão lógica) um assinante.
    
    Implementa a lógica de negócio para desativação de assinantes,
    mantendo o registro no banco para fins históricos.
    """
    
    def __init__(self, subscriber_repository: SubscriberRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            subscriber_repository: Uma implementação de SubscriberRepository
        """
        self.repository = subscriber_repository
    
    def execute(self, subscriber_id: UUID) -> bool:
        """
        Executa o caso de uso para desativar um assinante.
        
        Args:
            subscriber_id: ID do assinante a ser desativado
            
        Returns:
            bool: True se a operação foi bem-sucedida
            
        Raises:
            HTTPException: Se o assinante não for encontrado
        """
        # Verifica se o assinante existe
        subscriber = self.repository.get_by_id(subscriber_id)
        
        if not subscriber:
            raise HTTPException(
                status_code=404,
                detail=f"Assinante com ID {subscriber_id} não encontrado"
            )
        
        # Executa a desativação
        result = self.repository.delete(subscriber_id)
        
        if not result:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao desativar assinante com ID {subscriber_id}"
            )
        
        return True