"""
Entidades de domínio para Agendamentos (Appointments).
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional
from enum import Enum


class AppointmentStatus(str, Enum):
    """Enum para os possíveis status de um agendamento."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class AppointmentEntity:
    """
    Entidade de domínio rica para Agendamentos.
    
    Contém regras de negócio e validações específicas do domínio
    de agendamentos, como verificação de conflitos e transições de status.
    """
    
    def __init__(
        self,
        subscriber_id: UUID,
        patient_id: UUID,
        provider_id: UUID,
        service_id: UUID,
        start_time: datetime,
        end_time: datetime,
        status: str = AppointmentStatus.SCHEDULED,
        notes: Optional[str] = None,
        id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Inicializa uma nova entidade de Agendamento.
        
        Args:
            subscriber_id: ID do assinante (isolamento multitenancy)
            patient_id: ID do paciente
            provider_id: ID do profissional (médico, dentista, etc.)
            service_id: ID do serviço/procedimento
            start_time: Data e hora de início
            end_time: Data e hora de término
            status: Situação do agendamento (scheduled, confirmed, cancelled, completed)
            notes: Observações (opcional)
            id: UUID do agendamento, gerado automaticamente se não fornecido
            is_active: Indica se o agendamento está ativo
            created_at: Data de criação
            updated_at: Data da última atualização
        """
        self._validate_times(start_time, end_time)
        
        self.id = id if id else uuid4()
        self.subscriber_id = subscriber_id
        self.patient_id = patient_id
        self.provider_id = provider_id
        self.service_id = service_id
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.notes = notes
        self.is_active = is_active
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    def _validate_times(self, start_time: datetime, end_time: datetime) -> None:
        """
        Valida que o horário de início é anterior ao horário de término.
        
        Args:
            start_time: Data e hora de início
            end_time: Data e hora de término
            
        Raises:
            ValueError: Se a validação falhar
        """
        if start_time >= end_time:
            raise ValueError("O horário de término deve ser posterior ao horário de início")
    
    def update_status(self, new_status: str) -> None:
        """
        Atualiza o status do agendamento, verificando se a transição é válida.
        
        Args:
            new_status: Novo status para o agendamento
            
        Raises:
            ValueError: Se a transição de status não for permitida
        """
        # Validar transições de status (regras de negócio)
        valid_transitions = {
            AppointmentStatus.SCHEDULED: [AppointmentStatus.CONFIRMED, AppointmentStatus.CANCELLED],
            AppointmentStatus.CONFIRMED: [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED],
            AppointmentStatus.CANCELLED: [],  # Status final
            AppointmentStatus.COMPLETED: []   # Status final
        }
        
        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(
                f"Transição de status inválida: {self.status} -> {new_status}. "
                f"Transições permitidas: {valid_transitions.get(self.status, [])}"
            )
        
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def reschedule(self, start_time: datetime, end_time: datetime) -> None:
        """
        Reagenda o horário do agendamento, se permitido pelo status atual.
        
        Args:
            start_time: Novo horário de início
            end_time: Novo horário de término
            
        Raises:
            ValueError: Se o reagendamento não for permitido pelo status atual
                       ou se os horários forem inválidos
        """
        # Verificar se o status permite reagendamento
        if self.status in [AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED]:
            raise ValueError(f"Não é possível reagendar um agendamento com status {self.status}")
        
        # Validar novos horários
        self._validate_times(start_time, end_time)
        
        # Atualizar horários
        self.start_time = start_time
        self.end_time = end_time
        self.updated_at = datetime.utcnow()
    
    def cancel(self) -> None:
        """
        Cancela o agendamento, se permitido pelo status atual.
        
        Raises:
            ValueError: Se o cancelamento não for permitido pelo status atual
        """
        # Usar o método update_status para garantir validação de transição
        if self.status not in [AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]:
            raise ValueError(f"Não é possível cancelar um agendamento com status {self.status}")
        
        self.status = AppointmentStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def complete(self) -> None:
        """
        Marca o agendamento como concluído, se permitido pelo status atual.
        
        Raises:
            ValueError: Se a conclusão não for permitida pelo status atual
        """
        # Usar o método update_status para garantir validação de transição
        if self.status != AppointmentStatus.CONFIRMED:
            raise ValueError(f"Apenas agendamentos confirmados podem ser marcados como concluídos")
        
        self.status = AppointmentStatus.COMPLETED
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Converte a entidade para um dicionário.
        
        Returns:
            dict: Representação da entidade como dicionário
        """
        return {
            "id": str(self.id),
            "subscriber_id": str(self.subscriber_id),
            "patient_id": str(self.patient_id),
            "provider_id": str(self.provider_id),
            "service_id": str(self.service_id),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "status": self.status,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }