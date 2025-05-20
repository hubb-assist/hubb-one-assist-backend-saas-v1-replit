"""
Modelo SQLAlchemy para Planos e relação com Módulos.
"""
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Boolean, ForeignKey, Table, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


# Tabela associativa entre Planos e Módulos
plan_module = Table(
    "plan_modules",
    Base.metadata,
    Column("plan_id", UUID(as_uuid=True), ForeignKey("plans.id"), primary_key=True),
    Column("module_id", UUID(as_uuid=True), ForeignKey("modules.id"), primary_key=True),
    Column("config", JSONB, nullable=True),
)


class Plan(Base):
    """
    Modelo ORM para Planos.
    """
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    billing_cycle = Column(String, nullable=False)  # mensal, anual, etc
    is_active = Column(Boolean, default=True)
    public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    modules = relationship("Module", secondary=plan_module, back_populates="plans")


class PlanModule(Base):
    """
    Modelo ORM para configurações específicas de Módulos em Planos.
    """
    __tablename__ = "plan_module"

    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), primary_key=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), primary_key=True)
    config = Column(JSONB, nullable=True)