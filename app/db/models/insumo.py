"""
Modelo de banco de dados para Insumos.
"""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.db.session import Base


# Tabela de associação entre insumos e módulos
insumo_module = Table(
    'insumo_module',
    Base.metadata,
    Column('insumo_id', UUID(as_uuid=True), ForeignKey('insumos.id'), primary_key=True),
    Column('module_id', UUID(as_uuid=True), ForeignKey('modules.id'), primary_key=True)
)


class Insumo(Base):
    """Modelo SQLAlchemy para Insumos no banco de dados."""
    
    __tablename__ = "insumos"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(String(500), nullable=False)
    categoria = Column(String(50), nullable=False)
    valor_unitario = Column(Float, nullable=False)
    unidade_medida = Column(String(10), nullable=False)
    estoque_minimo = Column(Integer, nullable=False, default=0)
    estoque_atual = Column(Integer, nullable=False, default=0)
    fornecedor = Column(String(100), nullable=True)
    codigo_referencia = Column(String(50), nullable=True)
    data_validade = Column(DateTime, nullable=True)
    data_compra = Column(DateTime, nullable=True)
    observacoes = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com Subscriber (multitenant)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    subscriber = relationship("Subscriber", back_populates="insumos")
    
    # Relacionamento com Modules (muitos-para-muitos)
    modules = relationship("Module", secondary=insumo_module, back_populates="insumos")