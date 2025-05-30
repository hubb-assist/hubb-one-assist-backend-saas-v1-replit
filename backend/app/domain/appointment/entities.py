"""
Entidades de domínio para o módulo de Agendamentos
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4


class Appointment:
    """
    Entidade de domínio para Agendamento
    
    Representa um agendamento de consulta ou serviço para um paciente
    """
    
    def __init__(
        self,
        subscriber_id: UUID,
        patient_id: UUID,
        provider_id: UUID,
        service_name: str,
        start_time: datetime,
        end_time: datetime,
        status: str = "scheduled",
        notes: Optional[str] = None,
        id: Optional[UUID] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        """
        Inicializa uma nova instância de Appointment
        
        Args:
            subscriber_id: ID do assinante (empresa/clínica)
            patient_id: ID do paciente
            provider_id: ID do profissional
            service_name: Nome do serviço
            start_time: Data e hora de início
            end_time: Data e hora de término
            status: Status do agendamento (scheduled, confirmed, cancelled, completed)
            notes: Observações adicionais
            id: Identificador único, gerado automaticamente se não fornecido
            is_active: Indica se o registro está ativo
            created_at: Data e hora de criação
            updated_at: Data e hora da última atualização
        """
        self.id = id if id else uuid4()
        self.subscriber_id = subscriber_id
        self.patient_id = patient_id
        self.provider_id = provider_id
        self.service_name = service_name
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.notes = notes
        self.is_active = is_active
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()
        
        # Validar as regras de negócio
        self._validate()
    
    def _validate(self) -> None:
        """
        Valida as regras de negócio para a entidade Appointment
        
        Raises:
            ValueError: Se alguma regra de negócio for violada
        """
        if not self.service_name or len(self.service_name) < 3:
            raise ValueError("O nome do serviço é obrigatório e deve ter pelo menos 3 caracteres")
        
        if self.end_time <= self.start_time:
            raise ValueError("A data/hora de término deve ser posterior à data/hora de início")
        
        valid_statuses = ["scheduled", "confirmed", "cancelled", "completed"]
        if self.status not in valid_statuses:
            raise ValueError(f"Status inválido. Valores aceitos: {', '.join(valid_statuses)}")
        
        if self.status == "cancelled" and self.is_active:
            raise ValueError("Um agendamento cancelado não deveria estar ativo")
    
    def update(self, data: dict) -> None:
        """
        Atualiza os atributos do agendamento
        
        Args:
            data: Dicionário com os atributos a serem atualizados
            
        Raises:
            ValueError: Se alguma regra de negócio for violada após a atualização
        """
        if "service_name" in data and data["service_name"]:
            self.service_name = data["service_name"]
        
        if "start_time" in data and data["start_time"]:
            self.start_time = data["start_time"]
        
        if "end_time" in data and data["end_time"]:
            self.end_time = data["end_time"]
        
        if "status" in data and data["status"]:
            self.status = data["status"]
        
        if "notes" in data:
            self.notes = data["notes"]
        
        self.updated_at = datetime.utcnow()
        
        # Validar após as atualizações
        self._validate()
    
    def cancel(self) -> None:
        """
        Cancela o agendamento, alterando seu status para 'cancelled'
        
        Raises:
            ValueError: Se o agendamento já estiver concluído
        """
        if self.status == "completed":
            raise ValueError("Não é possível cancelar um agendamento já concluído")
        
        self.status = "cancelled"
        self.updated_at = datetime.utcnow()
    
    def complete(self) -> None:
        """
        Marca o agendamento como concluído
        
        Raises:
            ValueError: Se o agendamento estiver cancelado
        """
        if self.status == "cancelled":
            raise ValueError("Não é possível concluir um agendamento cancelado")
        
        self.status = "completed"
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """
        Desativa o agendamento (exclusão lógica)
        """
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """
        Converte a entidade para um dicionário
        
        Returns:
            dict: Dicionário com os atributos da entidade
        """
        return {
            "id": self.id,
            "subscriber_id": self.subscriber_id,
            "patient_id": self.patient_id,
            "provider_id": self.provider_id,
            "service_name": self.service_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "notes": self.notes,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }