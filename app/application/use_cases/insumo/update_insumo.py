"""
Caso de uso para atualização de insumos.
"""
from uuid import UUID
from fastapi import HTTPException, status

from app.domain.insumo.interfaces import InsumoRepository
from app.domain.insumo.entities import InsumoEntity
from app.schemas.insumo import InsumoUpdate


class UpdateInsumoUseCase:
    """
    Caso de uso para atualizar um insumo existente.
    """
    
    def __init__(self, insumo_repository: InsumoRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            insumo_repository: Uma implementação de InsumoRepository
        """
        self.repository = insumo_repository
    
    def execute(self, insumo_id: UUID, insumo_data: InsumoUpdate, subscriber_id: UUID) -> InsumoEntity:
        """
        Executa o caso de uso para atualizar um insumo.
        
        Args:
            insumo_id: ID do insumo a ser atualizado
            insumo_data: Dados a serem atualizados
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            InsumoEntity: Entidade de insumo atualizada
            
        Raises:
            HTTPException: Se o insumo não for encontrado ou houver erro na atualização
        """
        # Tentar atualizar o insumo
        updated_insumo = self.repository.update(insumo_id, insumo_data, subscriber_id)
        
        # Verificar se o insumo foi encontrado e atualizado
        if not updated_insumo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Insumo com ID {insumo_id} não encontrado"
            )
            
        return updated_insumo