"""
Caso de uso para obter um paciente por ID.
"""
from uuid import UUID
from typing import Optional

from app.domain.patient.interfaces import PatientRepository
from app.domain.patient.entities import PatientEntity


class GetPatientUseCase:
    """
    Caso de uso para buscar um paciente pelo ID.
    Segue o padrão de injeção de dependência recebendo o repositório.
    """
    
    def __init__(self, patient_repository: PatientRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            patient_repository: Uma implementação da interface PatientRepository
        """
        self.repository = patient_repository
    
    def execute(self, patient_id: UUID, subscriber_id: UUID) -> Optional[PatientEntity]:
        """
        Executa o caso de uso para obter um paciente por ID.
        
        Args:
            patient_id: ID do paciente a ser buscado
            subscriber_id: ID do assinante para isolamento multitenancy
            
        Returns:
            Optional[PatientEntity]: Entidade do paciente se encontrado, None caso contrário
        """
        return self.repository.get_by_id(patient_id, subscriber_id)