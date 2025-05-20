"""
Modelo SQLAlchemy para Usuários do sistema.
"""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    """
    Modelo ORM para Usuários.
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    permissions = Column(JSONB, nullable=True)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=True)
    segment_id = Column(UUID(as_uuid=True), ForeignKey("segments.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    subscriber = relationship("Subscriber", backref="users")
    segment = relationship("Segment", backref="users")