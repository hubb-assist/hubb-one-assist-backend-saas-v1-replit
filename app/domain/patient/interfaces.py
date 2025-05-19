"""
Interfaces abstratas para repositórios do domínio Patient.
Seguindo o Princípio de Inversão de Dependência (DIP).
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID

from app.domain.patient.entities import PatientEntity
from app.schemas.patient import PatientCreate, PatientUpdate


class PatientRepository(ABC):
    """
    Interface abstrata para o repositório de pacientes.
    Define os contratos que qualquer implementação deve seguir.
    """
    
    @abstractmethod
    def create(self, patient_data: PatientCreate, subscriber_id: UUID) -> PatientEntity:
        """
        Cria um novo paciente no repositório.
        
        Args:
            patient_data: Dados do paciente a ser criado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            PatientEntity: Entidade de paciente criada
        """
        pass
    
    @abstractmethod
    def get_by_id(self, patient_id: UUID, subscriber_id: UUID) -> Optional[PatientEntity]:
        """
        Busca um paciente pelo seu ID.
        
        Args:
            patient_id: ID do paciente a ser buscado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            Optional[PatientEntity]: Entidade de paciente se encontrada, None caso contrário
        """
        pass
    
    @abstractmethod
    def update(self, patient_id: UUID, patient_data: PatientUpdate, subscriber_id: UUID) -> PatientEntity:
        """
        Atualiza um paciente existente.
        
        Args:
            patient_id: ID do paciente a ser atualizado
            patient_data: Dados do paciente para atualização
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            PatientEntity: Entidade de paciente atualizada
        """
        pass
    
    @abstractmethod
    def list(
        self, 
        subscriber_id: UUID, 
        skip: int = 0, 
        limit: int = 10, 
        **filters
    ) -> Dict[str, Any]:
        """
        Lista pacientes com paginação e filtros.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenancy)
            skip: Quantidade de registros para pular
            limit: Limite de registros a retornar
            **filters: Filtros adicionais (ex: name, cpf)
            
        Returns:
            Dict[str, Any]: Objeto de resposta com lista de pacientes e metadados de paginação
        """
        pass
    
    @abstractmethod
    def delete(self, patient_id: UUID, subscriber_id: UUID) -> bool:
        """
        Exclui logicamente um paciente (is_active = False).
        
        Args:
            patient_id: ID do paciente a ser excluído
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            bool: True se a operação foi bem-sucedida, False caso contrário
        """
        pass