"""
Caso de uso para atualizar um agendamento existente.
"""
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.domain.appointment.entities import AppointmentEntity
from app.domain.appointment.interfaces import IAppointmentRepository


class UpdateAppointmentUseCase:
    """
    Caso de uso para atualizar um agendamento existente.
    
    Implementa a lógica de negócio para atualizar um agendamento,
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
        appointment_id: UUID,
        subscriber_id: UUID,
        patient_id: Optional[UUID] = None,
        provider_id: Optional[UUID] = None,
        service_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None
    ) -> AppointmentEntity:
        """
        Executa o caso de uso para atualizar um agendamento existente.
        
        Args:
            appointment_id: ID do agendamento a ser atualizado
            subscriber_id: ID do assinante (isolamento multitenancy)
            patient_id: Novo ID do paciente (opcional)
            provider_id: Novo ID do profissional (opcional)
            service_id: Novo ID do serviço/procedimento (opcional)
            start_time: Nova data e hora de início (opcional)
            end_time: Nova data e hora de término (opcional)
            status: Nova situação do agendamento (opcional)
            notes: Novas observações (opcional)
            
        Returns:
            AppointmentEntity: Entidade de agendamento atualizada
            
        Raises:
            ValueError: Se o agendamento não existir, houver conflito de horário ou dados inválidos
        """
        # Buscar o agendamento atual
        current_appointment = self.repository.get_by_id(appointment_id, subscriber_id)
        if not current_appointment:
            raise ValueError(f"Agendamento com ID {appointment_id} não encontrado")
        
        # Atualizar apenas os campos fornecidos
        if patient_id:
            current_appointment.patient_id = patient_id
        
        if provider_id:
            current_appointment.provider_id = provider_id
        
        if service_id:
            current_appointment.service_id = service_id
        
        # Verificar se ambos os horários foram fornecidos para atualização
        if (start_time and not end_time) or (end_time and not start_time):
            raise ValueError("Para reagendar, forneça tanto o horário de início quanto o de término")
        
        # Se novos horários foram fornecidos, usar o método reschedule da entidade
        if start_time and end_time:
            current_appointment.reschedule(start_time, end_time)
        
        # Se um novo status foi fornecido, usar o método update_status da entidade
        if status:
            current_appointment.update_status(status)
        
        # Atualizar notas se fornecidas
        if notes is not None:  # Permite string vazia ""
            current_appointment.notes = notes
        
        # Persistir as alterações
        return self.repository.update(current_appointment)