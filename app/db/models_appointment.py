"""
Modelo SQLAlchemy para a tabela de Agendamentos
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey, Boolean, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base

class Appointment(Base):
    """
    Modelo de Agendamento representando consultas marcadas para pacientes
    """
    __tablename__ = "appointments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_name = Column(String(255), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=False, default="scheduled")
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_at = Column(DateTime, nullable=False, server_default=text("now()"))

    # Relacionamentos
    subscriber = relationship("Subscriber", backref="appointments")
    patient = relationship("Patient", backref="appointments")
    provider = relationship("User", backref="appointments")