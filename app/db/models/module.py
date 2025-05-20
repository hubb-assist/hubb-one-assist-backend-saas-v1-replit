"""
Modelo SQLAlchemy para Módulos do sistema.
"""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.session import Base
from sqlalchemy.orm import relationship


class Module(Base):
    """
    Modelo ORM para Módulos do sistema.
    """
    __tablename__ = "modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    config = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    plans = relationship("Plan", secondary="plan_modules", back_populates="modules")