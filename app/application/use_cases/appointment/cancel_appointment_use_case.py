"""
Caso de uso para cancelar um agendamento.
"""
from uuid import UUID

from app.domain.appointment.entities import AppointmentEntity
from app.domain.appointment.interfaces import IAppointmentRepository


class CancelAppointmentUseCase:
    """
    Caso de uso para cancelar um agendamento.
    
    Implementa a lógica de negócio para cancelar um agendamento,
    garantindo que ele esteja em um status que permita cancelamento.
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório.
        
        Args:
            repository: Implementação de repositório de agendamentos
        """
        self.repository = repository
    
    def execute(self, appointment_id: UUID, subscriber_id: UUID) -> AppointmentEntity:
        """
        Executa o caso de uso para cancelar um agendamento.
        
        Args:
            appointment_id: ID do agendamento a ser cancelado
            subscriber_id: ID do assinante (isolamento multitenancy)
            
        Returns:
            AppointmentEntity: Entidade de agendamento cancelada
            
        Raises:
            ValueError: Se o agendamento não existir ou não puder ser cancelado
        """
        # Buscar o agendamento atual
        appointment = self.repository.get_by_id(appointment_id, subscriber_id)
        if not appointment:
            raise ValueError(f"Agendamento com ID {appointment_id} não encontrado")
        
        # Utilizar o método cancel da entidade (que já contém validação de status)
        appointment.cancel()
        
        # Persistir a alteração
        return self.repository.update(appointment)