"""
Modelos de banco de dados usando SQLAlchemy
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, Text, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, declarative_base

from app.db.session import Base

class UserRole(str, PyEnum):
    """Enum para roles de usuário no sistema"""
    SUPER_ADMIN = "SUPER_ADMIN"
    DIRETOR = "DIRETOR"
    COLABORADOR_NIVEL_2 = "COLABORADOR_NIVEL_2"
    DONO_ASSINANTE = "DONO_ASSINANTE"

class User(Base):
    """
    Modelo SQLAlchemy para a tabela de usuários
    """
    __tablename__ = "users"

    # Usando as colunas existentes no banco de dados
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.COLABORADOR_NIVEL_2)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # Relacionamento com Subscriber para usuários do tipo DONO_ASSINANTE
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=True)

    def __repr__(self):
        return f"<User {self.email}>"


class Segment(Base):
    """
    Modelo SQLAlchemy para a tabela de segmentos de mercado
    """
    __tablename__ = "segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False, unique=True, index=True)
    descricao = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Segment {self.nome}>"


class Module(Base):
    """
    Modelo SQLAlchemy para a tabela de módulos funcionais
    """
    __tablename__ = "modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String, nullable=False, unique=True, index=True)
    descricao = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Module {self.nome}>"


class Plan(Base):
    """
    Modelo SQLAlchemy para a tabela de planos
    """
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    segment_id = Column(UUID(as_uuid=True), ForeignKey("segments.id"), nullable=False)
    base_price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    segment = relationship("Segment", backref="plans")
    plan_modules = relationship("PlanModule", cascade="all, delete-orphan")
    
    # Propriedade para acessar módulos
    @property
    def modules(self):
        return [pm.module for pm in self.plan_modules]

    def __repr__(self):
        return f"<Plan {self.name}>"


class PlanModule(Base):
    """
    Tabela associativa entre Plan e Module com atributos adicionais
    """
    __tablename__ = "plan_modules"

    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), primary_key=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("modules.id"), primary_key=True)
    price = Column(Float, nullable=False, default=0.0)
    is_free = Column(Boolean, nullable=False, default=False)
    trial_days = Column(Integer, nullable=True)
    
    # Relacionamentos
    plan = relationship("Plan")
    module = relationship("Module")

    def __repr__(self):
        return f"<PlanModule {self.plan_id}:{self.module_id}>"


class Subscriber(Base):
    """
    Modelo SQLAlchemy para a tabela de assinantes do sistema
    """
    __tablename__ = "subscribers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)  # Nome do responsável
    clinic_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String)
    document = Column(String, unique=True)  # CPF ou CNPJ
    zip_code = Column(String)
    address = Column(String)
    number = Column(String)  # Número do endereço
    city = Column(String)
    state = Column(String)
    segment_id = Column(UUID(as_uuid=True), ForeignKey("segments.id"))
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    segment = relationship("Segment")
    plan = relationship("Plan")
    users = relationship("User", backref="subscriber")
    
    def __repr__(self):
        return f"<Subscriber {self.clinic_name}>"