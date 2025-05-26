from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Date, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

class CostClinical(Base):
    __tablename__ = "costs_clinical"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    procedure_name = Column(String(255), nullable=False)
    duration_hours = Column(Numeric(5, 2), nullable=False)
    hourly_rate = Column(Numeric(12, 2), nullable=False)
    total_cost = Column(Numeric(12, 2), nullable=False)
    date = Column(Date, nullable=False)
    observacoes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)