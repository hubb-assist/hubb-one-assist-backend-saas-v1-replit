"""
Modelo SQLAlchemy para Insumos e Módulos.
"""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.session import Base

# tabela associativa para modulos
insumo_modulo = Table(
    "insumo_modulo",
    Base.metadata,
    Column("insumo_id", UUID(as_uuid=True), ForeignKey("insumos.id"), primary_key=True),
    Column("modulo", String, primary_key=True),
)

class Insumo(Base):
    """
    Modelo ORM para Insumos.
    """
    __tablename__ = "insumos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    unidade = Column(String, nullable=False)
    valor = Column(Numeric(12, 2), nullable=False)
    observacoes = Column(String, nullable=True)
    categoria = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # relacionamento many-to-many simples via string de módulo
    modulos = relationship("Modulo", secondary=insumo_modulo, back_populates="insumos")

# Entidade auxiliar para módulos
class Modulo(Base):
    """
    Modelo ORM para Módulos.
    """
    __tablename__ = "modulos"

    name = Column(String, primary_key=True)
    insumos = relationship("Insumo", secondary=insumo_modulo, back_populates="modulos")