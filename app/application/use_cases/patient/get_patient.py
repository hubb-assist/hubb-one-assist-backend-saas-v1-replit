"""
Caso de uso para buscar um paciente específico.
"""
from uuid import UUID
from typing import Optional

from app.domain.patient.interfaces import PatientRepository
from app.domain.patient.entities import PatientEntity


class GetPatientUseCase:
    """
    Caso de uso para buscar um paciente pelo ID.
    Orquestra o processo de busca usando o repositório.
    """
    
    def __init__(self, patient_repository: PatientRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            patient_repository: Uma implementação de PatientRepository
        """
        self.repository = patient_repository
    
    def execute(self, patient_id: UUID, subscriber_id: UUID) -> Optional[PatientEntity]:
        """
        Executa o caso de uso para buscar um paciente.
        
        Args:
            patient_id: ID do paciente a ser buscado
            subscriber_id: ID do assinante para verificação de propriedade (multitenancy)
            
        Returns:
            Optional[PatientEntity]: Entidade de paciente se encontrada, None caso contrário
        """
        # Delegar a busca para o repositório
        return self.repository.get_by_id(patient_id, subscriber_id)