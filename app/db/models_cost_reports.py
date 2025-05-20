"""
Modelo de dados para relatórios de custos
"""
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Boolean, Column, String, DateTime, Date, ForeignKey, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class CostReport(Base):
    """
    Representa um relatório de custos gerado pelo sistema.
    """
    __tablename__ = "costs_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscriber_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Propriedades de período do relatório
    date_from = Column(Date, nullable=False)
    date_to = Column(Date, nullable=False)
    
    # Tipo do relatório (mensal, trimestral, anual, customizado)
    report_type = Column(String(50), nullable=False)
    
    # Valores totais calculados
    total_fixed_costs = Column(Numeric(10, 2), nullable=False, default=0)
    total_variable_costs = Column(Numeric(10, 2), nullable=False, default=0)
    total_clinical_costs = Column(Numeric(10, 2), nullable=False, default=0)
    total_supplies_costs = Column(Numeric(10, 2), nullable=False, default=0)
    grand_total = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Metadados
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Campos de controle
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<CostReport(id={self.id}, title={self.title}, from={self.date_from}, to={self.date_to})>"