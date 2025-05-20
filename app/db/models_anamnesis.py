from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

class Anamnesis(Base):
    __tablename__ = "anamneses"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subscriber_id   = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    patient_id      = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    chief_complaint = Column(Text, nullable=False)
    medical_history = Column(Text, nullable=True)
    allergies       = Column(Text, nullable=True)
    medications     = Column(Text, nullable=True)
    notes           = Column(Text, nullable=True)
    is_active       = Column(Boolean, default=True, nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)