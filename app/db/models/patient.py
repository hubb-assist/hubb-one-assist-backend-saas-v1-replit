"""
Modelo de banco de dados para pacientes.
"""
from uuid import UUID
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

from app.db.session import Base


class Patient(Base):
    """
    Modelo de banco de dados para pacientes.
    """
    __tablename__ = "patients"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, index=True)
    subscriber_id = Column(PGUUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    name = Column(String, nullable=False)
    cpf = Column(String, nullable=True, unique=True, index=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    address = Column(String, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    zip_code = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)