from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Integer, Date, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

class CostVariable(Base):
    __tablename__ = "costs_variable"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    nome = Column(String(255), nullable=False)
    valor_unitario = Column(Numeric(12, 2), nullable=False)
    quantidade = Column(Integer, nullable=False)
    data = Column(Date, nullable=False)
    observacoes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relacionamento com subscriber (se necessário mais tarde)
    # subscriber = relationship("Subscriber", back_populates="costs_variable")