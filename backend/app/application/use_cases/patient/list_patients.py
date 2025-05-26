"""
Caso de uso para listar pacientes com paginação e filtros.
"""
from uuid import UUID
from typing import Dict, Any, Optional

from app.domain.patient.interfaces import PatientRepository


class ListPatientsUseCase:
    """
    Caso de uso para listar pacientes com paginação e filtros.
    Orquestra o processo de listagem usando o repositório.
    """
    
    def __init__(self, patient_repository: PatientRepository):
        """
        Inicializa o caso de uso com uma implementação de repositório.
        
        Args:
            patient_repository: Uma implementação de PatientRepository
        """
        self.repository = patient_repository
    
    def execute(
        self, 
        subscriber_id: UUID, 
        skip: int = 0, 
        limit: int = 10, 
        name: Optional[str] = None,
        cpf: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executa o caso de uso para listar pacientes.
        
        Args:
            subscriber_id: ID do assinante para filtrar pacientes (multitenancy)
            skip: Número de registros para pular (para paginação)
            limit: Número máximo de registros a retornar
            name: Filtro opcional por nome do paciente
            cpf: Filtro opcional por CPF do paciente
            
        Returns:
            Dict[str, Any]: Dicionário contendo a lista de pacientes e metadados de paginação
        """
        # Preparar filtros dinâmicos
        filters = {}
        if name:
            filters["name"] = name
        if cpf:
            filters["cpf"] = cpf
            
        # Delegar para o repositório
        return self.repository.list(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            **filters
        )