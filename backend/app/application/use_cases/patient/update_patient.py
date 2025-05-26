"""
Caso de uso para atualizar dados de um paciente.
"""
from uuid import UUID

from fastapi import HTTPException, status

from app.domain.patient.interfaces import PatientRepository
from app.domain.patient.entities import PatientEntity
from app.schemas.patient import PatientUpdate


class UpdatePatientUseCase:
    """
    Caso de uso para atualizar um paciente existente.
    Orquestra o processo de atualização usando o repositório.
    """
    
    def __init__(self, patient_repository: PatientRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            patient_repository: Uma implementação de PatientRepository
        """
        self.repository = patient_repository
    
    def execute(self, patient_id: UUID, patient_data: PatientUpdate, subscriber_id: UUID) -> PatientEntity:
        """
        Executa o caso de uso para atualizar um paciente.
        
        Args:
            patient_id: ID do paciente a ser atualizado
            patient_data: Dados do paciente para atualização
            subscriber_id: ID do assinante para associação (multitenancy)
            
        Returns:
            PatientEntity: Entidade de paciente atualizada
            
        Raises:
            HTTPException: Se o paciente não for encontrado
        """
        # Verificar se o paciente existe
        patient = self.repository.get_by_id(patient_id, subscriber_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Paciente com ID {patient_id} não encontrado"
            )
        
        # Delegar a atualização para o repositório
        return self.repository.update(patient_id, patient_data, subscriber_id)