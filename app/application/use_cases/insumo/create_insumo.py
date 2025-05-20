"""
Caso de uso para criação de insumos.
"""
from uuid import UUID
from fastapi import HTTPException, status

from app.domain.insumo.interfaces import InsumoRepository
from app.domain.insumo.entities import InsumoEntity
from app.schemas.insumo import InsumoCreate


class CreateInsumoUseCase:
    """
    Caso de uso para criar um novo insumo.
    Orquestra o processo de criação usando o repositório.
    """
    
    def __init__(self, insumo_repository: InsumoRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            insumo_repository: Uma implementação de InsumoRepository
        """
        self.repository = insumo_repository
    
    def execute(self, insumo_data: InsumoCreate, subscriber_id: UUID) -> InsumoEntity:
        """
        Executa o caso de uso para criar um insumo.
        
        Args:
            insumo_data: Dados do insumo a ser criado
            subscriber_id: ID do assinante para associação (multitenancy)
            
        Returns:
            InsumoEntity: Entidade de insumo criada
            
        Raises:
            HTTPException: Se houver um erro na criação
        """
        try:
            return self.repository.create(insumo_data, subscriber_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Erro ao criar insumo: {str(e)}"
            )