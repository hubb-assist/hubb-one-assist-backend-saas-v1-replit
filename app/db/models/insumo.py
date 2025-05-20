"""
Modelo de banco de dados para Insumos.
"""
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.db.base_class import Base


class Insumo(Base):
    """
    Modelo de banco de dados para Insumos.
    """
    __tablename__ = "insumos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    unidade = Column(String, nullable=False)
    quantidade = Column(Float, nullable=False, default=0.0)
    observacoes = Column(String, nullable=True)
    categoria = Column(String, nullable=False)
    
    # Relações
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    modulo_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=True)
    
    # Metadados
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos SQLAlchemy
    subscriber = relationship("Subscriber", back_populates="insumos")
    modulo = relationship("Module", back_populates="insumos")