"""
Modelos de banco de dados para o módulo de Insumos.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class Insumo(Base):
    """
    Modelo de banco de dados para a entidade Insumo.
    
    Representa a tabela de insumos no banco de dados, 
    armazenando materiais, produtos e outros itens de estoque.
    """
    __tablename__ = "insumos"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    descricao = Column(String, nullable=False)
    categoria = Column(String, nullable=False, index=True)
    valor_unitario = Column(Float, nullable=False)
    unidade_medida = Column(String, nullable=False)
    estoque_minimo = Column(Integer, nullable=False, default=0)
    estoque_atual = Column(Integer, nullable=False, default=0)
    
    # Campos opcionais
    fornecedor = Column(String, nullable=True)
    codigo_referencia = Column(String, nullable=True)
    data_validade = Column(DateTime, nullable=True)
    data_compra = Column(DateTime, nullable=True)
    observacoes = Column(String, nullable=True)
    
    # Campos de controle
    subscriber_id = Column(PostgresUUID(as_uuid=True), index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    modules_used = relationship("InsumoModuleAssociation", back_populates="insumo", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Insumo(id={self.id}, nome='{self.nome}', categoria='{self.categoria}')>"


class InsumoModuleAssociation(Base):
    """
    Modelo de banco de dados para a associação entre Insumos e Módulos.
    
    Esta tabela representa a relação muitos-para-muitos entre
    insumos e módulos do sistema, com atributos adicionais.
    """
    __tablename__ = "insumo_module_associations"
    
    insumo_id = Column(PostgresUUID(as_uuid=True), ForeignKey("insumos.id", ondelete="CASCADE"), primary_key=True)
    module_id = Column(PostgresUUID(as_uuid=True), primary_key=True)
    
    quantidade_padrao = Column(Integer, nullable=False, default=1)
    observacao = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    insumo = relationship("Insumo", back_populates="modules_used")
    
    # Potencial relacionamento com Module (se existir)
    # module = relationship("Module")
    
    def __repr__(self):
        return f"<InsumoModuleAssociation(insumo_id={self.insumo_id}, module_id={self.module_id}, quantidade={self.quantidade_padrao})>"