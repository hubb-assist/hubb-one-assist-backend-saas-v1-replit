"""
Modelo de insumos para o banco de dados.
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Insumo(Base):
    """
    Modelo de insumo para o banco de dados.
    """
    __tablename__ = "insumos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    unidade = Column(String(30), nullable=False)
    quantidade = Column(Float, default=0.0, nullable=False)
    categoria = Column(String(50), nullable=False)
    modulo_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), nullable=True)
    observacoes = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    subscriber = relationship("Subscriber", back_populates="insumos")
    modulo = relationship("Module", back_populates="insumos")