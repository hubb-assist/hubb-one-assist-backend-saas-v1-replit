"""
Caso de uso para criação de pacientes.
"""
from uuid import UUID

from app.domain.patient.interfaces import PatientRepository
from app.domain.patient.entities import PatientEntity
from app.schemas.patient import PatientCreate


class CreatePatientUseCase:
    """
    Caso de uso para criação de novos pacientes no sistema.
    Orquestra o processo de criação usando o repositório.
    """
    
    def __init__(self, patient_repository: PatientRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            patient_repository: Uma implementação de PatientRepository
        """
        self.repository = patient_repository
    
    def execute(self, patient_data: PatientCreate, subscriber_id: UUID) -> PatientEntity:
        """
        Executa o caso de uso para criar um novo paciente.
        
        Args:
            patient_data: Dados do paciente a ser criado
            subscriber_id: ID do assinante para associação (multitenancy)
            
        Returns:
            PatientEntity: Entidade de paciente criada
        """
        # Aqui poderia ter validações adicionais de negócio
        # antes de delegar ao repositório
        
        return self.repository.create(patient_data, subscriber_id)