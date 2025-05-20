"""
Modelos SQLAlchemy para insumos e associações com módulos.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Insumo(Base):
    """
    Modelo SQLAlchemy para a tabela de insumos.
    
    Representa um insumo no banco de dados, com seus atributos
    e relacionamentos com outras entidades.
    """
    __tablename__ = "insumos"
    
    id = Column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    nome = Column(String(255), nullable=False, index=True)
    descricao = Column(Text, nullable=False)
    categoria = Column(String(100), nullable=False, index=True)
    valor_unitario = Column(Float, nullable=False)
    unidade_medida = Column(String(50), nullable=False)
    estoque_minimo = Column(Integer, nullable=False, default=0)
    estoque_atual = Column(Integer, nullable=False, default=0)
    fornecedor = Column(String(255), nullable=True)
    codigo_referencia = Column(String(100), nullable=True)
    data_validade = Column(DateTime, nullable=True)
    data_compra = Column(DateTime, nullable=True)
    observacoes = Column(Text, nullable=True)
    subscriber_id = Column(PgUUID(as_uuid=True), nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    modules_used = relationship("InsumoModuleAssociation", back_populates="insumo", cascade="all, delete-orphan")


class InsumoModuleAssociation(Base):
    """
    Modelo SQLAlchemy para a tabela de associação entre insumos e módulos.
    
    Representa uma relação muitos-para-muitos entre insumos e módulos,
    com atributos adicionais como quantidade padrão.
    """
    __tablename__ = "insumo_module_associations"
    
    insumo_id = Column(PgUUID(as_uuid=True), ForeignKey("insumos.id", ondelete="CASCADE"), primary_key=True)
    module_id = Column(PgUUID(as_uuid=True), ForeignKey("modules.id", ondelete="CASCADE"), primary_key=True)
    quantidade_padrao = Column(Integer, nullable=False, default=1)
    observacao = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    insumo = relationship("Insumo", back_populates="modules_used")
    module = relationship("Module")
    
    def __repr__(self):
        return f"<InsumoModuleAssociation insumo_id={self.insumo_id} module_id={self.module_id}>"