"""
Modelo SQLAlchemy para Assinantes do sistema.
"""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class Subscriber(Base):
    """
    Modelo ORM para Assinantes (clientes/organizações).
    """
    __tablename__ = "subscribers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    legal_name = Column(String, nullable=True)
    document = Column(String, nullable=True)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    segment_id = Column(UUID(as_uuid=True), ForeignKey("segments.id"), nullable=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=True)
    status = Column(String, nullable=False, default="pending")  # pending, active, suspended, cancelled
    config = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    segment = relationship("Segment", back_populates="subscribers")
    plan = relationship("Plan", back_populates="subscribers")