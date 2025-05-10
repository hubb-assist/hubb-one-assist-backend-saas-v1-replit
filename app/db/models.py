"""
Modelos de banco de dados usando SQLAlchemy
"""

import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, text
from sqlalchemy.dialects.postgresql import UUID

from app.db.session import Base

class UserRole(str, PyEnum):
    """Enum para roles de usuário no sistema"""
    SUPER_ADMIN = "SUPER_ADMIN"
    DIRETOR = "DIRETOR"
    COLABORADOR_NIVEL_1 = "COLABORADOR_NIVEL_1"
    COLABORADOR_NIVEL_2 = "COLABORADOR_NIVEL_2"
    CLIENTE = "CLIENTE"

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

    def __repr__(self):
        return f"<User {self.email}>"