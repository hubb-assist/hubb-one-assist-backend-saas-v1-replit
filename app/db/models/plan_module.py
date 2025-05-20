"""
Modelo para a relação entre Planos e Módulos (many-to-many).
"""
from sqlalchemy import Column, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func
from sqlalchemy import DateTime

from app.db.session import Base


class PlanModule(Base):
    """
    Modelo para a tabela que relaciona Planos e Módulos (relação muitos-para-muitos).
    Um plano pode ter vários módulos e um módulo pode estar em vários planos.
    """
    __tablename__ = "plan_modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(PGUUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)
    module_id = Column(PGUUID(as_uuid=True), ForeignKey("modules.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)