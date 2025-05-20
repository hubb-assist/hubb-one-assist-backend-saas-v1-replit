"""
Caso de uso para buscar um agendamento por ID.
"""
from uuid import UUID
from typing import Optional

from app.domain.appointment.entities import AppointmentEntity
from app.domain.appointment.interfaces import IAppointmentRepository


class GetAppointmentUseCase:
    """
    Caso de uso para buscar um agendamento por ID.
    """
    
    def __init__(self, repository: IAppointmentRepository):
        """
        Inicializa o caso de uso com um repositório.
        
        Args:
            repository: Implementação de repositório de agendamentos
        """
        self.repository = repository
    
    def execute(self, appointment_id: UUID, subscriber_id: UUID) -> Optional[AppointmentEntity]:
        """
        Executa o caso de uso para buscar um agendamento por ID.
        
        Args:
            appointment_id: ID do agendamento
            subscriber_id: ID do assinante (para isolamento multitenancy)
            
        Returns:
            Optional[AppointmentEntity]: Entidade encontrada ou None se não existir
            
        Raises:
            ValueError: Se os parâmetros forem inválidos
        """
        # Validações básicas
        if not appointment_id:
            raise ValueError("ID do agendamento é obrigatório")
        
        if not subscriber_id:
            raise ValueError("ID do assinante é obrigatório")
        
        # Buscar no repositório
        return self.repository.get_by_id(appointment_id, subscriber_id)