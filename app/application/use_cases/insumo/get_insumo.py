"""
Caso de uso para obter insumos por ID.
"""
from uuid import UUID
from fastapi import HTTPException, status

from app.domain.insumo.interfaces import InsumoRepository
from app.domain.insumo.entities import InsumoEntity


class GetInsumoUseCase:
    """
    Caso de uso para obter um insumo pelo ID.
    """
    
    def __init__(self, insumo_repository: InsumoRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            insumo_repository: Uma implementação de InsumoRepository
        """
        self.repository = insumo_repository
    
    def execute(self, insumo_id: UUID, subscriber_id: UUID) -> InsumoEntity:
        """
        Executa o caso de uso para obter um insumo pelo ID.
        
        Args:
            insumo_id: ID do insumo a ser buscado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            InsumoEntity: Entidade de insumo encontrada
            
        Raises:
            HTTPException: Se o insumo não for encontrado
        """
        insumo = self.repository.get_by_id(insumo_id, subscriber_id)
        
        if not insumo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insumo com ID {insumo_id} não encontrado"
            )
            
        return insumo