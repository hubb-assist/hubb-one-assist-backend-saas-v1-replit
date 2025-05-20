"""
Caso de uso para exclusão lógica de insumos.
"""
from uuid import UUID
from fastapi import HTTPException, status

from app.domain.insumo.interfaces import InsumoRepository


class DeleteInsumoUseCase:
    """
    Caso de uso para desativar um insumo logicamente.
    """
    
    def __init__(self, insumo_repository: InsumoRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            insumo_repository: Uma implementação de InsumoRepository
        """
        self.repository = insumo_repository
    
    def execute(self, insumo_id: UUID, subscriber_id: UUID) -> bool:
        """
        Executa o caso de uso para desativar um insumo.
        
        Args:
            insumo_id: ID do insumo a ser desativado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            bool: True se desativado com sucesso
            
        Raises:
            HTTPException: Se o insumo não for encontrado
        """
        # Tentar desativar o insumo
        success = self.repository.delete(insumo_id, subscriber_id)
        
        # Verificar se o insumo foi encontrado e desativado
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insumo com ID {insumo_id} não encontrado"
            )
            
        return True