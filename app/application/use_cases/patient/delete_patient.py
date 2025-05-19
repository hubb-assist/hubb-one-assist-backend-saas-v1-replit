"""
Caso de uso para excluir logicamente um paciente.
"""
from uuid import UUID

from fastapi import HTTPException, status

from app.domain.patient.interfaces import PatientRepository


class DeletePatientUseCase:
    """
    Caso de uso para excluir logicamente um paciente (desativação).
    Orquestra o processo de exclusão lógica usando o repositório.
    """
    
    def __init__(self, patient_repository: PatientRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            patient_repository: Uma implementação de PatientRepository
        """
        self.repository = patient_repository
    
    def execute(self, patient_id: UUID, subscriber_id: UUID) -> bool:
        """
        Executa o caso de uso para excluir logicamente um paciente.
        
        Args:
            patient_id: ID do paciente a ser excluído
            subscriber_id: ID do assinante para associação (multitenancy)
            
        Returns:
            bool: True se a operação foi bem-sucedida
            
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
        
        # Delegar a exclusão lógica para o repositório
        return self.repository.delete(patient_id, subscriber_id)