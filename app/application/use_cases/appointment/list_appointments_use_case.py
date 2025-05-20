"""
Caso de uso para listar agendamentos com paginação e filtros.
"""
from uuid import UUID
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.domain.appointment.entities import AppointmentEntity
from app.domain.appointment.interfaces import IAppointmentRepository


class ListAppointmentsUseCase:
    """
    Caso de uso para listar agendamentos.
    
    Implementa a lógica de negócio para buscar agendamentos,
    permitindo paginação e aplicação de diversos filtros.
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório.
        
        Args:
            repository: Implementação de repositório de agendamentos
        """
        self.repository = repository
    
    def execute(
        self,
        subscriber_id: UUID,
        skip: int = 0,
        limit: int = 100,
        patient_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None,
        service_id: Optional[UUID] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[AppointmentEntity]:
        """
        Executa o caso de uso para listar agendamentos.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenancy)
            skip: Quantidade de registros para pular (paginação)
            limit: Quantidade máxima de registros para retornar
            patient_id: Filtro por ID do paciente (opcional)
            provider_id: Filtro por ID do profissional (opcional)
            service_id: Filtro por ID do serviço/procedimento (opcional)
            status: Filtro por status do agendamento (opcional)
            date_from: Filtro por data inicial (opcional)
            date_to: Filtro por data final (opcional)
            
        Returns:
            List[AppointmentEntity]: Lista de entidades de agendamento
        """
        # Construir os filtros a partir dos parâmetros opcionais
        filters: Dict[str, Any] = {}
        
        if patient_id:
            filters['patient_id'] = patient_id
        
        if provider_id:
            filters['provider_id'] = provider_id
        
        if service_id:
            filters['service_id'] = service_id
        
        if status:
            filters['status'] = status
        
        if date_from:
            filters['date_from'] = date_from
        
        if date_to:
            filters['date_to'] = date_to
        
        # Delegar para o repositório
        return self.repository.list(
            subscriber_id=subscriber_id,
            skip=skip,
            limit=limit,
            filters=filters
        )