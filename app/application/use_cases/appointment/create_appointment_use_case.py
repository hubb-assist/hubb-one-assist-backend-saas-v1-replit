"""
Caso de uso para criar um novo agendamento.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.domain.appointment.entities import AppointmentEntity
from app.domain.appointment.interfaces import IAppointmentRepository


class CreateAppointmentUseCase:
    """
    Caso de uso para criar um novo agendamento.
    
    Implementa a lógica de negócio para criar um agendamento,
    validando regras como conflitos de horário e restrições de status.
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
        patient_id: UUID,
        provider_id: UUID,
        service_id: UUID,
        start_time: datetime,
        end_time: datetime,
        status: str = "scheduled",
        notes: Optional[str] = None
    ) -> AppointmentEntity:
        """
        Executa o caso de uso para criar um novo agendamento.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenancy)
            patient_id: ID do paciente
            provider_id: ID do profissional (médico, dentista, etc.)
            service_id: ID do serviço/procedimento
            start_time: Data e hora de início
            end_time: Data e hora de término
            status: Situação do agendamento (scheduled, confirmed, cancelled, completed)
            notes: Observações (opcional)
            
        Returns:
            AppointmentEntity: Entidade de agendamento criada
            
        Raises:
            ValueError: Se houver conflito de horário ou dados inválidos
        """
        # Criar entidade de agendamento (já inclui validações básicas)
        appointment = AppointmentEntity(
            subscriber_id=subscriber_id,
            patient_id=patient_id,
            provider_id=provider_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time,
            status=status,
            notes=notes
        )
        
        # Persistir no repositório (incluindo verificação de conflitos)
        return self.repository.create(appointment)