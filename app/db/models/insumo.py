"""
Modelo SQLAlchemy para Insumos do sistema.
"""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Modulo(Base):
    """
    Modelo ORM para Módulos de categorias de insumos.
    """
    __tablename__ = "insumo_modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    insumos = relationship("Insumo", back_populates="modulo")


class Insumo(Base):
    """
    Modelo ORM para Insumos do sistema (materiais, medicamentos, equipamentos).
    """
    __tablename__ = "insumos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # medicamento, material, equipamento
    unidade = Column(String, nullable=False)  # unidade de medida (ampola, caixa, unidade)
    quantidade = Column(Float, default=0)
    observacoes = Column(String, nullable=True)
    categoria = Column(String, nullable=False)
    modulo_id = Column(UUID(as_uuid=True), ForeignKey("insumo_modules.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    modulo = relationship("Modulo", back_populates="insumos")