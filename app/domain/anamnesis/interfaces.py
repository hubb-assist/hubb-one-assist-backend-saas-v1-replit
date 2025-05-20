from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.anamnesis.entities import AnamnesisEntity
from app.schemas.anamnesis_schema import AnamnesisCreate, AnamnesisUpdate

class IAnamnesisRepository(ABC):
    """
    Interface para repositório de anamneses.
    Define os métodos que qualquer implementação de repositório deve fornecer.
    """
    
    @abstractmethod
    def create(self, data: AnamnesisCreate, patient_id: UUID, subscriber_id: UUID) -> AnamnesisEntity:
        """
        Cria uma nova anamnese.
        
        Args:
            data: Dados da anamnese
            patient_id: ID do paciente
            subscriber_id: ID do assinante (multi-tenant)
            
        Returns:
            AnamnesisEntity: Entidade criada
        """
        pass
    
    @abstractmethod
    def get_by_id(self, id: UUID, subscriber_id: UUID) -> Optional[AnamnesisEntity]:
        """
        Busca uma anamnese pelo ID.
        
        Args:
            id: ID da anamnese
            subscriber_id: ID do assinante (multi-tenant)
            
        Returns:
            Optional[AnamnesisEntity]: Entidade encontrada ou None
        """
        pass
    
    @abstractmethod
    def list_by_patient(
        self, patient_id: UUID, subscriber_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[AnamnesisEntity]:
        """
        Lista anamneses de um paciente específico.
        
        Args:
            patient_id: ID do paciente
            subscriber_id: ID do assinante (multi-tenant)
            skip: Quantidade de registros para pular (paginação)
            limit: Limite de registros a retornar
            
        Returns:
            List[AnamnesisEntity]: Lista de entidades
        """
        pass
    
    @abstractmethod
    def update(self, id: UUID, data: AnamnesisUpdate, subscriber_id: UUID) -> Optional[AnamnesisEntity]:
        """
        Atualiza uma anamnese existente.
        
        Args:
            id: ID da anamnese
            data: Dados da anamnese para atualização
            subscriber_id: ID do assinante (multi-tenant)
            
        Returns:
            Optional[AnamnesisEntity]: Entidade atualizada ou None
        """
        pass
    
    @abstractmethod
    def delete(self, id: UUID, subscriber_id: UUID) -> bool:
        """
        Exclui logicamente uma anamnese.
        
        Args:
            id: ID da anamnese
            subscriber_id: ID do assinante (multi-tenant)
            
        Returns:
            bool: True se a exclusão foi bem-sucedida
        """
        pass
    
    @abstractmethod
    def count_by_patient(self, patient_id: UUID, subscriber_id: UUID) -> int:
        """
        Conta o número de anamneses de um paciente.
        
        Args:
            patient_id: ID do paciente
            subscriber_id: ID do assinante (multi-tenant)
            
        Returns:
            int: Quantidade de anamneses
        """
        pass