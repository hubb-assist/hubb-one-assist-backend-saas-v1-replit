from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Date, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

class Receivable(Base):
    __tablename__ = "receivables"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    patient_id    = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    description   = Column(String(255), nullable=False)
    amount        = Column(Numeric(12, 2), nullable=False)
    due_date      = Column(Date, nullable=False)
    received      = Column(Boolean, default=False, nullable=False)
    receive_date  = Column(DateTime, nullable=True)
    notes         = Column(Text, nullable=True)
    is_active     = Column(Boolean, default=True, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)