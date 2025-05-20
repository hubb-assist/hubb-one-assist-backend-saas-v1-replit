"""
Modelo SQLAlchemy para Agendamentos (Appointments).
"""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Appointment(Base):
    """
    Modelo de banco de dados para Agendamentos.
    
    Representa um agendamento marcado por um paciente com um profissional de saúde,
    contendo informações como horário, status, serviço e observações.
    """
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False, index=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="scheduled")
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos (opcional, ajuda com queries ORM)
    # patient = relationship("Patient", back_populates="appointments")
    # provider = relationship("User", back_populates="provider_appointments")
    
    def __init__(
        self,
        subscriber_id,
        patient_id,
        provider_id,
        service_id,
        start_time,
        end_time,
        status="scheduled",
        notes=None,
        id=None,
        is_active=True,
        created_at=None,
        updated_at=None
    ):
        """
        Inicializa um novo Agendamento.
        
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