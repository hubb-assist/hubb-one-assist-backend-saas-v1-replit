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
    # Permissões personalizadas - armazenadas como Array de strings
    custom_permissions = Column(Text, nullable=True)  # Armazenado como JSON
    # Relacionamento com Subscriber para usuários do tipo DONO_ASSINANTE
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=True)
    
    @property
    def permissions(self):
        """Obtém a lista de permissões personalizadas do usuário"""
        import json
        if not self.custom_permissions:
            return []
        try:
            return json.loads(self.custom_permissions)
        except:
            return []
    
    @permissions.setter
    def permissions(self, permissions_list):
        """Define as permissões personalizadas do usuário"""
        import json
        if permissions_list is None:
            self.custom_permissions = None
        else:
            self.custom_permissions = json.dumps(list(set(permissions_list)))

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
    arduino_devices = relationship("ArduinoDevice", back_populates="subscriber")
    
    def __repr__(self):
        return f"<Subscriber {self.clinic_name}>"


class ArduinoDevice(Base):
    """
    Modelo para dispositivos Arduino vinculados a assinantes
    """
    __tablename__ = "arduino_devices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    mac_address = Column(String(17), nullable=False, unique=True, index=True)
    ip_address = Column(String(45), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    firmware_version = Column(String(50), nullable=True)
    last_connection = Column(DateTime, nullable=True)
    
    # Relacionamento com assinante
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("subscribers.id"), nullable=False)
    subscriber = relationship("Subscriber", back_populates="arduino_devices")
    
    # Campos de auditoria
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ArduinoDevice {self.name} ({self.device_id})>"