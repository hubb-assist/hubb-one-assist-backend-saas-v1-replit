from typing import Dict, List, Any, Optional
from uuid import UUID

from app.domain.anamnesis.interfaces import IAnamnesisRepository
from app.schemas.anamnesis_schema import AnamnesisCreate, AnamnesisUpdate

class CreateAnamnesisUseCase:
    """
    Caso de uso para criar uma nova anamnese para um paciente.
    """
    
    def __init__(self, repository: IAnamnesisRepository):
        self.repository = repository
    
    def execute(self, data: AnamnesisCreate, patient_id: UUID, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - cria uma nova anamnese.
        
        Args:
            data: Dados da anamnese
            patient_id: ID do paciente
            subscriber_id: ID do assinante (multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário representando a anamnese criada
            
        Raises:
            ValueError: Se houver erro de validação ou criação
        """
        try:
            anamnesis_entity = self.repository.create(data, patient_id, subscriber_id)
            return anamnesis_entity.to_dict()
        except Exception as e:
            raise ValueError(f"Erro ao criar anamnese: {str(e)}")

class GetAnamnesisUseCase:
    """
    Caso de uso para buscar uma anamnese específica.
    """
    
    def __init__(self, repository: IAnamnesisRepository):
        self.repository = repository
    
    def execute(self, id: UUID, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - busca uma anamnese por ID.
        
        Args:
            id: ID da anamnese
            subscriber_id: ID do assinante (multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário representando a anamnese
            
        Raises:
            ValueError: Se a anamnese não for encontrada
        """
        anamnesis_entity = self.repository.get_by_id(id, subscriber_id)
        if not anamnesis_entity:
            raise ValueError(f"Anamnese com ID {id} não encontrada")
        return anamnesis_entity.to_dict()

class ListAnamnesisUseCase:
    """
    Caso de uso para listar anamneses de um paciente.
    """
    
    def __init__(self, repository: IAnamnesisRepository):
        self.repository = repository
    
    def execute(
        self, patient_id: UUID, subscriber_id: UUID, skip: int = 0, limit: int = 100
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso - lista anamneses de um paciente.
        
        Args:
            patient_id: ID do paciente
            subscriber_id: ID do assinante (multi-tenant)
            skip: Quantidade de registros para pular (paginação)
            limit: Limite de registros a retornar
            
        Returns:
            Dict[str, Any]: Dicionário com itens e total
        """
        anamnesis_list = self.repository.list_by_patient(
            patient_id, subscriber_id, skip, limit
        )
        total = self.repository.count_by_patient(patient_id, subscriber_id)
        
        return {
            "items": [anamnesis.to_dict() for anamnesis in anamnesis_list],
            "total": total
        }

class UpdateAnamnesisUseCase:
    """
    Caso de uso para atualizar uma anamnese.
    """
    
    def __init__(self, repository: IAnamnesisRepository):
        self.repository = repository
    
    def execute(self, id: UUID, data: AnamnesisUpdate, subscriber_id: UUID) -> Dict[str, Any]:
        """
        Executa o caso de uso - atualiza uma anamnese.
        
        Args:
            id: ID da anamnese
            data: Dados da anamnese para atualização
            subscriber_id: ID do assinante (multi-tenant)
            
        Returns:
            Dict[str, Any]: Dicionário representando a anamnese atualizada
            
        Raises:
            ValueError: Se a anamnese não for encontrada ou houver erro de validação
        """
        anamnesis_entity = self.repository.update(id, data, subscriber_id)
        if not anamnesis_entity:
            raise ValueError(f"Anamnese com ID {id} não encontrada")
        return anamnesis_entity.to_dict()

class DeleteAnamnesisUseCase:
    """
    Caso de uso para excluir (logicamente) uma anamnese.
    """
    
    def __init__(self, repository: IAnamnesisRepository):
        self.repository = repository
    
    def execute(self, id: UUID, subscriber_id: UUID) -> bool:
        """
        Executa o caso de uso - exclui logicamente uma anamnese.
        
        Args:
            id: ID da anamnese
            subscriber_id: ID do assinante (multi-tenant)
            
        Returns:
            bool: True se a exclusão foi bem-sucedida
            
        Raises:
            ValueError: Se a anamnese não for encontrada
        """
        result = self.repository.delete(id, subscriber_id)
        if not result:
            raise ValueError(f"Anamnese com ID {id} não encontrada")
        return True