
"""
Modelo ORM para pacientes no sistema.
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Date, DateTime, Boolean, ForeignKey, UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Patient(Base):
    """
    Modelo para pacientes no sistema, vinculados a assinantes.
    """
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(150), nullable=False, index=True)
    cpf = Column(String(14), nullable=False, index=True)
    rg = Column(String(20), nullable=True)
    birth_date = Column(Date, nullable=False)
    phone = Column(String(20), nullable=True)

    # Endereço
    zip_code = Column(String(10), nullable=True)
    address = Column(String(150), nullable=True)
    number = Column(String(20), nullable=True)
    complement = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(2), nullable=True)

    # Relacionamento com assinante (multitenant)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    subscriber = relationship("Subscriber", backref="patients")
    
    # Campos de auditoria
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
